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

const radikoUrlChecker = (url) => {
    console.log(url)

    fetch(url)
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.status + " " + response.statusText)
            }
            return response.json()
        })
        .then((json) => {
            if (json.status == 'success') {
                // console.log(json)
                if (confirm(json.data.program_name +
                        '\n' + json.data.broadcaster +
                        '\n' + json.data.started_at +
                        ' 〜 ' + json.data.ended_at)) {
                    alert('ここで処理する予定')
                }
            } else if (json.status == 'error') {
                // TODO errorの場合をとfailで分岐（その前に、運用方針があってるか相談）
                console.log(json)
                alert('エラーです')
            } else {
                alert('想定外のエラー！')
            }
        })
        .catch((error) => {
            alert("すんません、エラーでしたわ！\n\n↓↓エラー内容↓↓\n" + error)
        })
}

const fetchAndReload = (url, message = "") => {
    if (!!message) {
        const result = window.confirm(message)
        if (!result) {
            return
        }
    }
    // console.log(url)
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
        })
}