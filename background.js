// function injectedFunction() {
//     console.log("injectedFunction");
//     // document.body.style.backgroundColor = 'orange';
// }

// chrome.webNavigation.onCompleted.addListener((tab) => {
//     console.log("onCompleted ==> tab:" + JSON.stringify(tab));
//     chrome.scripting.executeScript({
//         target: { tabId: tab.tabId },
//         // files: ['content-script.js'],
//         function: injectedFunction
//     });
// });

console.log("background.js");

chrome.storage.sync.get(['rules'], function(result) {
    console.log('[background] rules: ' + JSON.stringify(result.rules));
    if (!result.rules) {
        chrome.storage.sync.set({
            "rules": []
        }, function() {
            console.log('rules set to ' + String([]));
        });
    }
});

chrome.contextMenus.create({ title: 'My menu', id: 'my_menu' });

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId = 'my_menu') {
        console.log("my_menu onClicked:", info);
    }
})

// chrome.tabs.onActivated.addListener((activeInfo) => {
//     chrome.tabs.get(activeInfo.tabId, function(tab) {
//         console.log(tabs);
//     });
// });





// chrome.tabs.onActivated.addListener((activeInfo) => {
//     console.log(activeInfo);
//     chrome.tabs.get(activeInfo.tabId, function(tab) {
//         console.log(tab);
//         chrome.scripting.executeScript({
//             target: { tabId: tab.id },
//             files: ['content-script.js']
//         });
//     });
// });