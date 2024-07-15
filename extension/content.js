function extractContent() {
  let web_url = document.URL;
  let content = document.body.innerHTML;
  return { web_url, content };
}

function showIndicator() {
  const indicator = document.createElement('div');
  indicator.textContent = 'You\'ve visited this page before!';
  indicator.style.position = 'fixed';
  indicator.style.top = '5px';
  indicator.style.right = '5px';
  indicator.style.backgroundColor = '#F0FFFF';
  indicator.style.fontSize = '12px',
    indicator.style.padding = '2px';
  document.body.appendChild(indicator);
}


function storeContentInLocalStorage(web_url, content) {
  chrome.storage.local.get('storage_container', function (result) {
    const storage_container = result.storage_container || {}; // get previous content

    if (web_url in storage_container) {
      showIndicator();
    } else {
      // URL does not exist in local storage, store the new URL's content
      storage_container[web_url] = content;
      chrome.storage.local.set({ storage_container: storage_container }, function () {
        if (chrome.runtime.lastError) {
          console.error('Error setting local storage:', chrome.runtime.lastError);
        } else {
          console.log('Content stored successfully.');
        }
      });
    }
  });
}

const { web_url, content } = extractContent();
const urlObj = new URL(web_url);
if (!urlObj.searchParams.has('q')) { // to not store webpages with search results
  storeContentInLocalStorage(web_url, content);
}


