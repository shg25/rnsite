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

const fetchAndReload = url => {
    console.log(url)
    fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.status + " " + response.statusText)
            }
            return response.json()
        })
        .then((data) => {
            console.log(data)
            location.reload()
        })
        .catch((error) => {
            alert("すんません、エラーでしたわ！\n\n↓↓エラー内容↓↓\n" + error)
        });
}