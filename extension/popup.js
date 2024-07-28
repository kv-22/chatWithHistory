const server_url = 'http://127.0.0.1:8000'

document.getElementById('ask').onclick = async () => { // async to use await 
  try {

    const question = document.getElementById('question').value;
    if (question) {
      const response_query = await fetch(server_url + '/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          "question": question
        })
      });
      const data_query = await response_query.json();
      console.log(data_query.answer);
      const text = data_query.answer['gpt_answer'];
      console.log(text);
      const urls = data_query.answer['urls'];
      let resultDiv = document.getElementById('answer');

      // Clear any existing content in resultDiv
      resultDiv.innerHTML = '';

      if (text) {

        // Display text
        resultDiv.innerText = text + "\n\nSources:\n\n";

        // Display URLs
        urls.forEach(url => {
          if (isValidURL(url)) {
            let anchor = document.createElement('a');
            anchor.href = url;
            anchor.textContent = url;
            anchor.target = '_blank'; // Open link in a new tab

            // Add the anchor element and a line break to resultDiv
            resultDiv.appendChild(anchor);
            resultDiv.appendChild(document.createElement('br'));
            resultDiv.appendChild(document.createElement('br'));
          }
        });

      } else {
        resultDiv.innerText = 'None of the websites you visited answered the query :(';

      }

    }
  } catch (error) {
    console.log(error.message);
  }
};

function isValidURL(text) {
  try {
    new URL(text); // create new url object
    return true; // if url was correct no error
  } catch (e) {
    return false;
  }
}
