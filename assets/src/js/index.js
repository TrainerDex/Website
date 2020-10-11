import React from 'react';
import ReactDOM from "react-dom";

const api_base = "/api/v1/leaderboard/"
const globlb = api_base+"v1.1/"

const stats = {
  total_xp: {identifier: 'total_xp', verbose_name: 'Total XP'},
  travel_km: {identifier: 'badge_travel_km', verbose_name: 'Distance Walked'},
}

function leaderboardUrl(stat) {
  return globlb+stat["identifier"]+'/';
}

var stat = 'total_xp'

function makeTitle(stat) {
  return (
    <div>
      <h1>{stat["verbose_name"]} Leaderboard</h1>
    </div>
  );
}

ReactDOM.render(
  makeTitle(stats[stat]),
  document.getElementById('content')
);
