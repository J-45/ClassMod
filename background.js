console.log("Chilling");

chrome.storage.sync.set({
    "rules": [
        ["d1|s1|r1"],
        ["d2|s2|r2"]
    ]
}, function() {
    console.log('Value is set to ' + String([
        ["d1|s1|r1"],
        ["d2|s2|r2"]
    ]));
});

chrome.storage.sync.get(['rules'], function(result) {
    console.log('Value currently is ' + result.rules);
});

chrome.action.onClicked.addListener(function(tab) {
    chrome.action.setTitle({ tabId: tab.id, title: "You are on tab:" + tab.id });
});

chrome.contextMenus.create({ title: 'My menu', id: 'my_menu' });

chrome.contextMenus.onClicked.addListener(function(info, tab) {
    if (info.menuItemId = 'my_menu') {
        console.log(info);
    }
})