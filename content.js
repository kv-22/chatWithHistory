let web_url = document.URL;
let content = document.body.innerText.trim();
content = content.replace(/\s+/g, ' ').trim(); // remove new lines and space
chrome.storage.local.get(['storage_container'], result => {
  const storage_container = result.storage_container || {}; // get previous content 
  storage_container[web_url] = content; // store the new url's content
  chrome.storage.local.set(storage_container); // store in the local storage
});