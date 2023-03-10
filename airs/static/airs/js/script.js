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

const getCookie = name => {
    let cookieValue = null
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';')
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim()
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
                break
            }
        }
    }
    return cookieValue
}
const csrftoken = getCookie('csrftoken')


const radikoUrlChecker = (program_name, check_url, create_url) => {
    fetch(check_url)
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.status + " " + response.statusText)
            }
            return response.json()
        })
        .then((json) => {
            if (json.status == 'success') {
                const message1 = '以下の内容で登録しますか？' +
                    '\n' + json.data.program_name +
                    '\n' + json.data.broadcaster +
                    '\n' + json.data.started_at +
                    ' 〜 ' + json.data.ended_at
                if (confirm(message1)) {
                    // 番組名が違ったら更に確認する
                    let message2 = ''
                    if (program_name != json.data.program_name) {
                        message2 = '番組名が前回と違うけど大丈夫？' +
                            '\n前回：' + program_name +
                            '\n今回：' + json.data.program_name
                    }

                    // titleを使った放送登録処理に進む
                    const body = new URLSearchParams()
                    body.append('radiko_title', json.data.radiko_title)
                    postAndReload(create_url, message2, body, function (data) {
                        if (data.status = 'success' && data.data.next_url) {
                            location.href = data.data.next_url
                        } else {
                            location.reload()
                        }
                    })
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
            console.log(error)
            alert("すんません、エラーでしたわ！\n\n↓↓エラー内容↓↓\n" + error)
        })
}

const postAndReload = (url, message = "", body = new URLSearchParams(), callback) => {
    if (!!message) {
        const result = window.confirm(message)
        if (!result) {
            return
        }
    }
    fetch(url, {
            method: 'POST',
            body: body,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
                'X-CSRFToken': csrftoken,
            },
        })
        .then((response) => {
            if (!response.ok) {
                throw new Error(response.status + " " + response.statusText)
            }
            return response.json()
        })
        .then((data) => {
            // console.log(data)
            if (callback) {
                callback(data)
            } else {
                location.reload()
            }
        })
        .catch((error) => {
            console.log(error)
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