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

// TODO まだ使ってない
const submitTextarea = (textarea_id, url) => {
    // const text = document.getElementById('textarea_nanitozo_comment_recommend').value
    const text = document.getElementById(textarea_id).value
    // copyToClipboardAndShowAlert(text)
    window.location.replace(url)

    // document.getElementById("span3").textContent = ta3;
}