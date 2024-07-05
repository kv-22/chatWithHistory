const apiKey = 'YOUR OPENAI API KEY HERE';

document.getElementById('ask').onclick = async () => { // async to use await 
  try {
    let combined_text = await getCombinedText(); // wait until promise is resolved
    const question = document.getElementById('question').value;
    const userPrompt = `${combined_text}\n\nQuestion: ${question}\nProvide only the URLs of the webites that mention what I asked for. If none of the websites contain what I asked return 'None'`;
    console.log(userPrompt);
    messages = [{ "role": "system", "content": "You are a helpful assitant" },
    { "role": "user", "content": userPrompt }];

    try {
      if (question) {
        const response = await fetch('https://api.openai.com/v1/chat/completions', { // wait until response arrives
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            "model": "gpt-3.5-turbo",
            "messages": messages
          })
        });
        const data = await response.json();
        const text = data.choices[0].message.content;

        if (text != 'None') {
          const urls = text.split(/\s+/);
          let resultDiv = document.getElementById('answer');
          resultDiv.innerHTML = '';

          // for displaying each url as a link and making them redirectable 
          urls.forEach(url => {
            let anchor = document.createElement('a');
            anchor.href = url;
            anchor.textContent = url;
            anchor.target = '_blank'; // Open link in a new tab
            resultDiv.appendChild(anchor);

            // Add a line break for better readability
            resultDiv.appendChild(document.createElement('br'));
          });

        } else {
          document.getElementById('answer').innerText = text;

        }

      }
    } catch (error) {
      console.log(error.message);
    }

  } catch (error) {
    console.error("Error retrieving combined text:", error);
  }


};

function getCombinedText() {
  return new Promise((resolve, reject) => { // async operation, use promise instead of callback
    chrome.storage.local.get(null, result => { // null gets everything in local storage
      let combined_text = "";
      for (let key in result) {
        if (result.hasOwnProperty(key) && isValidURL(key)) {
          combined_text += "Website: " + key + "\nContent: " + result[key] + "\n\n";
        }
      }
      resolve(combined_text);
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



