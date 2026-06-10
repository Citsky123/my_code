
// 仅限超星尔雅 考试详情页面
let download=true
chrome.action.onClicked.addListener(async (e)=>{  
    if(download){
        chrome.scripting.executeScript({
            target: {
                tabId: e.id
            },
            files: ['js/jquery.min.js','js/xlsx.core.min.js','js/cs.js']
        })
        download=false
    }  
    await chrome.tabs.sendMessage(e.id, { 
        extension: 'download' 
    })
})