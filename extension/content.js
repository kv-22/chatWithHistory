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
  indicator.style.zIndex = 9999;
  document.body.appendChild(indicator);
}


function storeContentInLocalStorage(web_url, content) {
  chrome.storage.local.get('storage_container', async function (result) {
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

      // send to background to send to backend
      chrome.runtime.sendMessage({
        action: 'parseAndStore',
        payload: { web_url, content }
      }, function (response) {
        console.log(response.success);
        if (response && response.success) {
          console.log('Content parsed and stored successfully.');
        } else {
          console.error('Error parsing or storing content:', response.error);
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


