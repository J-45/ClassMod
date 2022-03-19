console.log("content-script.js");
// document.body.style.backgroundColor = 'orange';
// let d = document;
// console.log('document.body: ' + document.body);

chrome.storage.sync.get(['rules'], function(result) {
    console.log('[content] rules: ' + JSON.stringify(result.rules));
    if (!result.rules) {
        console.log('No rules !');
        return;
    }

    for (let i = 0; i < result.rules.length; i++) {
        console.log('Rule: ' + JSON.stringify(result.rules[i]));
        let oldclass = result.rules[i][1];
        let newclass = result.rules[i][1];
        // console.log('document: ' + document);
        let selected_elements = document.getElementsByClassName(oldclass);
        console.log('oldclass: ' + oldclass);
        for (let i = 0; i < selected_elements.length; i++) {
            console.log('selected_elements[i]: ' + JSON.stringify(selected_elements[i], null, 4));
            selected_elements[i].classList.remove(oldclass);
            selected_elements[i].classList.add(newclass);
        }
        // console.log('selected_element: ' + selected_element[0].innerHTML);

        // selected_element.classList.remove(oldclass);
        // selected_element.classList.add(newclass);
    }
});