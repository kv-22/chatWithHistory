const server_url = 'http://127.0.0.1:8000'

chrome.runtime.onMessage.addListener(async function(message, sender, sendResponse) {
    if (message.action === 'parseAndStore') {
      const { web_url, content } = message.payload;
  
      // send to server for parsing and storing in vector db
      try {
        const response = await fetch(server_url + '/parse', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            "url_and_content": {
              [web_url]: content
            }
          })
        });
  
        if (!response.ok) {
          throw new Error('Server response was not ok.');
        }
  
        const data = await response.text();
        console.log(data);
        sendResponse({ success: true });
      } catch (error) {
        console.error('Error fetching or parsing:', error);
        sendResponse({ success: false, error: error.message });
      }
      
      return true;
    }
  });
  