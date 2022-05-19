window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

const deleteBtn = document.getElementById('deleteBtn')
deleteBtn.onclick = function (e) {
  venueId = e.target.dataset['id']
  fetch('/venues/' + venueId, { method: 'DELETE' })
    .then(res => {
      return res.json()
    })
    .then(jsonRes => {
      console.log('Success: ' + jsonRes.success)
      window.location.replace('/');
    })
    .catch(e => {
      console.log(e)
    })
}