#!/usr/bin/env node

/**
 * 高機能PostgreSQLバックアップスクリプト
 * - 週1回自動実行
 * - データサイズ比較による異常検知
 * - 前回バックアップファイルの自動削除
 * - Slack通知機能
 */

const { exec } = require('child_process');
const AWS = require('aws-sdk');
const fs = require('fs').promises;
const path = require('path');

// 環境変数
const {
  DATABASE_URL,
  AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY,
  AWS_S3_BUCKET,
  AWS_S3_REGION = 'ap-northeast-1',
  BACKUP_SIZE_THRESHOLD = 50, // 50%の変化でアラート
  SLACK_WEBHOOK_URL,
  BACKUP_PREFIX = 'weekly-backup'
} = process.env;

// AWS S3設定
const s3 = new AWS.S3({
  accessKeyId: AWS_ACCESS_KEY_ID,
  secretAccessKey: AWS_SECRET_ACCESS_KEY,
  region: AWS_S3_REGION
});

/**
 * PostgreSQL dump実行
 */
async function createDump() {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5); // 2025-08-31T15-44-32
  const filename = `${BACKUP_PREFIX}-${timestamp}.sql`;
  
  console.log(`📦 Creating database dump: ${filename}`);
  
  return new Promise((resolve, reject) => {
    // PostgreSQL v17対応: 複数のpg_dumpオプションを試行
    const dumpCommands = [
      `pg_dump "${DATABASE_URL}" --no-password --compress=0 --verbose > ${filename}`,
      `pg_dump "${DATABASE_URL}" --compress=0 > ${filename}`,
      `pg_dump "${DATABASE_URL}" > ${filename}`
    ];
    
    const tryDumpCommand = (commandIndex) => {
      if (commandIndex >= dumpCommands.length) {
        reject(new Error('All pg_dump methods failed'));
        return;
      }
      
      exec(dumpCommands[commandIndex], async (error, stdout, stderr) => {
        if (error) {
          console.log(`⚠️ Command ${commandIndex + 1} failed, trying next...`);
          tryDumpCommand(commandIndex + 1);
          return;
        }
      
      try {
        const stats = await fs.stat(filename);
        const sizeInMB = (stats.size / (1024 * 1024)).toFixed(2);
        console.log(`✅ Dump completed: ${sizeInMB}MB`);
        
        resolve({
          filename,
          size: stats.size,
          sizeInMB: parseFloat(sizeInMB)
        });
      } catch (statError) {
        reject(statError);
      }
      });
    };
    
    tryDumpCommand(0);
  });
}

/**
 * 前回バックアップサイズを取得
 */
async function getPreviousBackupSize() {
  try {
    const objects = await s3.listObjectsV2({
      Bucket: AWS_S3_BUCKET,
      Prefix: BACKUP_PREFIX
    }).promise();
    
    if (objects.Contents.length === 0) {
      console.log('📝 No previous backup found');
      return null;
    }
    
    // 最新のファイルを取得
    const latest = objects.Contents
      .sort((a, b) => b.LastModified - a.LastModified)[0];
    
    console.log(`📊 Previous backup: ${(latest.Size / (1024 * 1024)).toFixed(2)}MB`);
    return {
      size: latest.Size,
      key: latest.Key
    };
  } catch (error) {
    console.error('⚠️ Failed to get previous backup size:', error);
    return null;
  }
}

/**
 * サイズ変化をチェック
 */
function checkSizeChange(currentSize, previousSize) {
  if (!previousSize) {
    return { isNormal: true, changePercent: 0 };
  }
  
  const changePercent = Math.abs((currentSize - previousSize.size) / previousSize.size * 100);
  const isNormal = changePercent <= BACKUP_SIZE_THRESHOLD;
  
  console.log(`📈 Size change: ${changePercent.toFixed(1)}% (threshold: ${BACKUP_SIZE_THRESHOLD}%)`);
  
  return { isNormal, changePercent };
}

/**
 * Slack通知送信
 */
async function sendSlackNotification(message) {
  console.log(`🔍 Slack notification called with message: "${message}"`);
  console.log(`🔍 SLACK_WEBHOOK_URL length: ${SLACK_WEBHOOK_URL ? SLACK_WEBHOOK_URL.length : 'undefined'}`);
  
  if (!SLACK_WEBHOOK_URL || SLACK_WEBHOOK_URL === 'https://hooks.slack.com/your/webhook/url') {
    console.log('📢 Slack notification skipped (no valid webhook URL)');
    return;
  }
  
  try {
    const https = require('https');
    const data = JSON.stringify({
      text: `🛡️ Database Backup Alert: ${message}`
    });
    
    const url = new URL(SLACK_WEBHOOK_URL);
    const options = {
      hostname: url.hostname,
      port: url.port || 443,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    };
    
    return new Promise((resolve, reject) => {
      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            console.log('📱 Slack notification sent successfully');
            resolve();
          } else {
            console.error(`📱 Slack API error ${res.statusCode}: ${body}`);
            resolve(); // エラーでもプロセスを継続
          }
        });
      });
      
      req.on('error', (error) => {
        console.error('📱 Failed to send Slack notification:', error.message);
        resolve(); // エラーでもプロセスを継続
      });
      
      req.write(data);
      req.end();
    });
  } catch (error) {
    console.error('📱 Slack notification error:', error.message);
  }
}

/**
 * S3にファイルアップロード
 */
async function uploadToS3(filename, filesize) {
  try {
    const fileBuffer = await fs.readFile(filename);
    
    const uploadParams = {
      Bucket: AWS_S3_BUCKET,
      Key: filename,
      Body: fileBuffer,
      ServerSideEncryption: 'AES256',
      Metadata: {
        'backup-size': filesize.toString(),
        'backup-date': new Date().toISOString()
      }
    };
    
    console.log(`☁️ Uploading to S3: ${filename}`);
    await s3.upload(uploadParams).promise();
    console.log('✅ Upload completed');
    
    return true;
  } catch (error) {
    console.error('❌ S3 upload failed:', error);
    throw error;
  }
}

/**
 * 前回バックアップファイルを削除
 */
async function deletePreviousBackup(previousBackup) {
  if (!previousBackup) {
    console.log('🗑️ No previous backup to delete');
    return;
  }
  
  try {
    await s3.deleteObject({
      Bucket: AWS_S3_BUCKET,
      Key: previousBackup.key
    }).promise();
    
    console.log(`🗑️ Deleted previous backup: ${previousBackup.key}`);
  } catch (error) {
    console.error('⚠️ Failed to delete previous backup:', error);
  }
}

/**
 * ローカルファイル削除
 */
async function cleanupLocalFile(filename) {
  try {
    await fs.unlink(filename);
    console.log(`🧹 Cleaned up local file: ${filename}`);
  } catch (error) {
    console.error('⚠️ Failed to cleanup local file:', error);
  }
}

/**
 * メイン処理
 */
async function main() {
  console.log('🚀 Starting smart backup process...');
  console.log(`📅 ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}`);
  
  try {
    // 1. 前回バックアップサイズ取得
    const previousBackup = await getPreviousBackupSize();
    
    // 2. データベースダンプ
    const dumpResult = await createDump();
    
    // 3. サイズチェック
    const sizeCheck = checkSizeChange(dumpResult.size, previousBackup);
    
    // 4. 異常検知時の通知
    if (!sizeCheck.isNormal) {
      const message = `Database size changed by ${sizeCheck.changePercent.toFixed(1)}% (${dumpResult.sizeInMB}MB)`;
      console.log(`🚨 Sending Slack notification: ${message}`);
      await sendSlackNotification(message);
      console.log('⚠️ Size change detected, but backup continues...');
    } else {
      console.log(`✅ Normal size change: ${sizeCheck.changePercent.toFixed(1)}% (within ${BACKUP_SIZE_THRESHOLD}% threshold)`);
    }
    
    // 5. S3アップロード
    await uploadToS3(dumpResult.filename, dumpResult.size);
    
    // 6. 前回ファイル削除（サイズ異常時は保持）
    if (sizeCheck.isNormal) {
      await deletePreviousBackup(previousBackup);
    } else {
      console.log(`🛡️ Size anomaly detected (${sizeCheck.changePercent.toFixed(1)}% change). Previous backup preserved for safety.`);
    }
    
    // 7. ローカルファイルクリーンアップ
    await cleanupLocalFile(dumpResult.filename);
    
    console.log('🎉 Smart backup completed successfully!');
    
    // 8. 成功通知（常に送信）
    const successMessage = `Weekly backup completed: ${dumpResult.sizeInMB}MB (${sizeCheck.changePercent.toFixed(1)}% change)`;
    console.log(`🚨 Sending success notification...`);
    await sendSlackNotification(successMessage);
    
    if (sizeCheck.isNormal) {
      console.log(`✅ Weekly backup: ${dumpResult.sizeInMB}MB (${sizeCheck.changePercent.toFixed(1)}% change)`);
    }
    
  } catch (error) {
    console.error('💥 Backup failed:', error);
    
    // エラー通知
    await sendSlackNotification(`Backup failed: ${error.message}`);
    process.exit(1);
  }
}

// 実行
if (require.main === module) {
  main();
}

module.exports = { main };