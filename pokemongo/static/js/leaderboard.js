// TrainerDex.app
// Copyright 2020 TurnrDev
// Script version: v1.0
// This is made for the leaderboard API v1.1

var main = document.getElementById("content")
var params = new URLSearchParams(window.location.search);

// Set default params
params.set("stat", params.get("stat") || "total_xp")
params.set("page", params.get("page") || 1)

// define basic information about the api
var apiVersion = 1
if (window.location.host == '127.0.0.1:8000') {
  console.warn("TrainerDex: The hostname is a debug hostname. This script will continue assuming you have a local database set up.")
  var apiDomain = window.location.host
} else {
  var apiDomain = 'trainerdex.app'
}
var apiBase = `${window.location.protocol}//${apiDomain}/api/v${apiVersion}/`


function toggleSpinner(targetState = null) {
  let spinner = document.getElementById("spinner")
  var currentState = spinner.classList.contains("is-active")
  console.debug(`toggleSpinner: currentState is ${currentState}`);

  if (targetState === null) {
    if (currentState == true) {
      targetState = false
    } else {
      targetState = true
    }
  }
  console.debug(`toggleSpinner: targetState is ${targetState}`);


  console.debug(`toggleSpinner: changing currentState to ${targetState}`);
  if (targetState == true) {
      spinner.classList.add("is-active");
    } else {
      spinner.classList.remove("is-active");
  }
  var currentState = spinner.classList.contains("is-active")
  console.debug(`toggleSpinner: currentState changed to ${currentState}`);
};

function updateParamsInURL() {
  let newURL = `${window.location.protocol}//${window.location.host}${window.location.pathname}?${params.toString()}`
  if (newURL != window.location) {
    window.history.pushState({path:newURL},'',newURL);
  }
}


function getAPIUrl() {
  console.log(`TrainerDex: building api query url`);
  let stat = params.get("stat")
  return `${apiBase}leaderboard/v1.1/${stat}/`;
}

const downloadLeaderboard = async() => {
  let r = await fetch(getAPIUrl());
  leaderboard =  await r.json();
}

function preRenderLeaderboard() {
  table = document.createElement("table");
  table.className = "mdl-data-table mdl-js-data-table mdl-shadow--2dp"
  table.createTHead();
  table.createTBody();
  let header = table.tHead.insertRow(0);
  header.insertCell(0); // The position row, no name
  header.insertCell(1);
  header.cells[1].innerHTML = "Trainer"
  header.cells[1].className = "mdl-data-table__cell--non-numeric"
  header.insertCell(2);
  header.cells[2].innerHTML = "Level"
  header.insertCell(3);
  header.cells[3].innerHTML = "Team"
  header.insertCell(4);
  header.cells[4].innerHTML = params.get("stat")
  header.cells[4].className = "mdl-data-table__header--sorted-descending"
  main.appendChild(table);
  componentHandler.upgradeElement(table);
}

preRenderLeaderboard()

function renderLeaderboard(entries) {
  entries.forEach(function (e, i) {
    let row = table.tBodies[0].insertRow();
    // Position
    row.insertCell(0);
    row.cells[0].innerHTML = e.position
    // Trainer
    row.insertCell(1);
    row.cells[1].innerHTML = e.username
    // Level
    row.insertCell(2);
    row.cells[2].innerHTML = e.level
    // Team
    row.insertCell(3);
    row.cells[3].innerHTML = e.faction.name_en
    // Value
    row.insertCell(4);
    row.cells[4].innerHTML = e.value
  })
  componentHandler.upgradeElement(table);
}

const downloadAndRender = async() => {
  toggleSpinner(true);
  await downloadLeaderboard();
  updateParamsInURL();
  renderLeaderboard(leaderboard.leaderboard);
  toggleSpinner(false);
}

downloadAndRender()
