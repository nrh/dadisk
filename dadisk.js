function toggle_subs()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "?action=toggle_subs", false);
  xhr.send(null);
  var target_div = document.getElementById('status');
  target_div.innerHTML = '<pre>' + xhr.responseText + '</pre>';
}

function toggle_play()
{
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "?action=toggle_play", false);
  xhr.send(null);
  var target_div = document.getElementById('status');
  target_div.innerHTML = '<pre>' + xhr.responseText + '</pre>';
}

function play_file(target)
{
  var xhr = new XMLHttpRequest();
  var data = new FormData();
  var target_div = document.getElementById('status');
  data.append('target', target);
  data.append('action', 'play');
  xhr.open("POST", "#", false);
  xhr.send(data);
  target_div.innerHTML = '<pre>' + xhr.responseText + '</pre>';
}

