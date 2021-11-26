// クリップボードにコピー（IEはNG & 画面にフォーカスが当たってないとNG）
const copyToClipboard = text => {
    navigator.clipboard.writeText(text)
}

// クリップボードにコピーしてアラートを表示
const copyToClipboardAndShowAlert = text => {
    copyToClipboard(text)

    // 普通にAlertやConfirmを実行するとフォーカスが外れてコピーが機能しないので別スレッドで処理する
    setTimeout(() => {
        window.alert(text + ' をたぶんコピーしました（IEは無理っぽい）')
    }, 0)
}