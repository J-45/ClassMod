document.getElementById("btn").addEventListener("click", async() => {
    let new_dom = document.getElementById('new_dom').value;
    let new_s = document.getElementById('new_s').value;
    let new_r = document.getElementById('new_r').value;

    let tbodyRef = document.getElementById('rules').getElementsByTagName('tbody')[0];
    let newRow = tbodyRef.insertRow(1);
    let newCell1 = newRow.insertCell(0);
    let newCell2 = newRow.insertCell(1);
    let newCell3 = newRow.insertCell(2);
    newCell1.appendChild(document.createTextNode(new_dom));
    newCell2.appendChild(document.createTextNode('"' + new_s + '"'));
    newCell3.appendChild(document.createTextNode('"' + new_r + '"'));

    chrome.storage.sync.get(['rules'], function(result) {
        console.log('Value currently is ' + result.rules);
        // btn.innerHTML = result.rules;
    });

    document.getElementById('new_dom').value = '';
    document.getElementById('new_s').value = '';
    document.getElementById('new_r').value = '';
});

function filter(text) {
    console.log('search_input onkeypress:' + text);
}