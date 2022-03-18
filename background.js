console.log("lets go");

chrome.storage.sync.get(['rules'], function(result) {
    console.log('rules: ' + JSON.stringify(result.rules));
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


chrome.tabs.query({
    active: true,
    currentWindow: true
}, function(tabs) {
    var tab = tabs[0];
    console.log(tab);
    var url = tab.url;

    var gettingCurrent = browser.tabs.getCurrent()
    console.log(gettingCurrent);
});