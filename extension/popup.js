const server_url = 'http://127.0.0.1:8000'

document.getElementById('ask').onclick = async () => { // async to use await 
  try {
    let content = await getContent(); // wait until promise is resolved
    console.log(content);
    const question = document.getElementById('question').value;

    try {
      if (question) {
        const response = await fetch(server_url + '/parse', { // wait until response arrives
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            "url_and_content": content
          })
        });
        const data = await response.text();
        console.log(data);


        const response_query = await fetch(server_url + '/query_history', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            "question": question
          })
        });
        const data_query = await response_query.json();
        const text = data_query.answer['response'];
        console.log(text);

        if (text != 'None') {
          const urls = text.split(/\s+/);

          let resultDiv = document.getElementById('answer');
          resultDiv.innerHTML = '';

          // for displaying each url as a link and making them redirectable 
          urls.forEach(url => {
            if (isValidURL(url)) {
              let anchor = document.createElement('a');
              anchor.href = url;
              anchor.textContent = url;
              anchor.target = '_blank'; // Open link in a new tab
              resultDiv.appendChild(anchor);

              // Add a line break for better readability
              resultDiv.appendChild(document.createElement('br'));

            }

          });

        } else {
          document.getElementById('answer').innerText = text;

        }

      }
    } catch (error) {
      console.log(error.message);
    }

  } catch (error) {
    console.error("Error retrieving content:", error);
  }


};

function getContent() {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get('storage_container', result => {
      let content_dict = {};
      const storage_container = result.storage_container || {}; // get the storage container

      for (let key in storage_container) {
        content_dict[key] = storage_container[key];
      }

      resolve(content_dict);
    });
  });
}

function isValidURL(text) {
  try {
    new URL(text); // create new url object
    return true; // if url was correct no error
  } catch (e) {
    return false;
  }
}



