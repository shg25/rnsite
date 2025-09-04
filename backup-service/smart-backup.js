#!/usr/bin/env node

/**
 * PostgreSQL スマートバックアップサービス
 * 
 * 機能:
 * - PostgreSQLデータベースの自動バックアップ
 * - サイズ異常検知とアラートシステム
 * - 前回バックアップの安全な削除機能
 * - 3パターンSlack通知システム
 * - AWS S3暗号化ストレージ
 */

const { exec } = require('child_process');
const AWS = require('aws-sdk');
const fs = require('fs').promises;

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
 * タイムスタンプ付きPostgreSQLデータベースダンプを作成
 * @returns {Object} ファイル名、サイズ、MB単位サイズを含むダンプ結果
 */
async function createDump() {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const filename = `${BACKUP_PREFIX}-${timestamp}.sql`;
  
  console.log(`📦 Creating database dump: ${filename}`);
  
  return new Promise((resolve, reject) => {
    // PostgreSQL v17サーバーと古いpg_dumpクライアント間の互換性問題対応
    // Railwayのサーバー：v17.6、コンテナのpg_dump：v16系（2025年時点）
    // pg_dumpクライアントとサーバーのバージョン不一致時に失敗する可能性があるため、段階的にフォールバック
    const dumpCommands = [
      `pg_dump "${DATABASE_URL}" --no-password --compress=0 --verbose > ${filename}`, // 最新機能版（v17対応）
      `pg_dump "${DATABASE_URL}" --compress=0 > ${filename}`,                         // 基本版（圧縮無効）
      `pg_dump "${DATABASE_URL}" > ${filename}`                                       // 最小限版（最高互換性）
    ];
    
    const tryDumpCommand = (commandIndex) => {
      if (commandIndex >= dumpCommands.length) {
        reject(new Error('All pg_dump methods failed'));
        return;
      }
      
      exec(dumpCommands[commandIndex], async (error) => {
        if (error) {
          console.log(`⚠️ pg_dumpコマンド ${commandIndex + 1} が失敗（バージョン互換性問題の可能性）、代替コマンドを試行...`);
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
 * S3から前回のバックアップ情報を取得
 * @returns {Object|null} 前回のバックアップデータまたはnull（見つからない場合）
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
    
    // 最新のバックアップファイルを取得
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
 * バックアップサイズ変化率をチェック
 * @param {number} currentSize - 現在のバックアップサイズ（バイト）
 * @param {Object|null} previousSize - 前回のバックアップ情報
 * @returns {Object} isNormalとchangePercentを含むサイズチェック結果
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
 * Slack webhookへ通知を送信
 * @param {string} message - 送信するメッセージ
 */
async function sendSlackNotification(message) {
  
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
    
    return new Promise((resolve) => {
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
 * バックアップファイルをAWS S3に暗号化してアップロード
 * @param {string} filename - アップロードするローカルファイル名
 * @param {number} filesize - ファイルサイズ（バイト）
 * @returns {boolean} アップロード成功ステータス
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
 * S3から前回のバックアップファイルを削除
 * @param {Object|null} previousBackup - 前回のバックアップ情報
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
 * ローカル一時バックアップファイルをクリーンアップ
 * @param {string} filename - 削除するローカルファイル
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
 * メインバックアップ処理の実行
 * 完全なバックアップワークフローを統制
 */
async function main() {
  console.log('🚀 Starting smart backup process...');
  console.log(`📅 ${new Date().toLocaleString('ja-JP', { timeZone: 'Asia/Tokyo' })}`);
  
  try {
    // 1. 前回バックアップ情報を取得
    const previousBackup = await getPreviousBackupSize();
    
    // 2. データベースダンプを作成
    const dumpResult = await createDump();
    
    // 3. サイズ変化をチェック
    const sizeCheck = checkSizeChange(dumpResult.size, previousBackup);
    
    // 4. サイズチェック結果をログ出力
    if (!sizeCheck.isNormal) {
      console.log('⚠️ Size change detected, but backup continues...');
    } else {
      console.log(`✅ Normal size change: ${sizeCheck.changePercent.toFixed(1)}% (within ${BACKUP_SIZE_THRESHOLD}% threshold)`);
    }
    
    // 5. S3にアップロード
    await uploadToS3(dumpResult.filename, dumpResult.size);
    
    // 6. 前回バックアップを削除（サイズ異常検知時は保持）
    if (sizeCheck.isNormal) {
      await deletePreviousBackup(previousBackup);
    } else {
      console.log(`🛡️ Size anomaly detected (${sizeCheck.changePercent.toFixed(1)}% change). Previous backup preserved for safety.`);
    }
    
    // 7. ローカルファイルをクリーンアップ
    await cleanupLocalFile(dumpResult.filename);
    
    console.log('🎉 Smart backup completed successfully!');
    
    // 8. Slack通知を送信（3パターン：正常、異常、エラー）
    let notificationMessage;
    
    if (!sizeCheck.isNormal) {
      // パターン3: バックアップ成功だがサイズ異常を検知
      notificationMessage = `⚠️ Weekly backup completed with size anomaly: ${dumpResult.sizeInMB}MB (${sizeCheck.changePercent.toFixed(1)}% change from previous backup). Previous backup preserved for safety.`;
    } else {
      // パターン1: バックアップ成功（正常）
      notificationMessage = `✅ Weekly backup completed successfully: ${dumpResult.sizeInMB}MB (${sizeCheck.changePercent.toFixed(1)}% change from previous backup). Previous backup deleted.`;
    }
    
    await sendSlackNotification(notificationMessage);
    
  } catch (error) {
    console.error('💥 Backup failed:', error);
    
    // パターン2: バックアップ失敗
    const errorMessage = `❌ Weekly backup failed: ${error.message}. Please check the system immediately.`;
    await sendSlackNotification(errorMessage);
    process.exit(1);
  }
}

// 直接実行サポート
if (require.main === module) {
  main();
}

module.exports = { main };