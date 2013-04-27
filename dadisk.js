function toggle_subs()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "?action=toggle_subs", false);
  xhr.send(null);
  var target_div = document.getElementById('status');
  target_div.innerHTML = xhr.responseText;
}

function toggle_play()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "?action=toggle_play", false);
  xhr.send(null);
  var target_div = document.getElementById('status');
  target_div.innerHTML = xhr.responseText;
}

function play_file(target)
{
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "?action=play", false);
  xhr.send(target);
  var target_div = document.getElementById('status');
  target_div.innerHTML = xhr.responseText;
}

