// data/make_chart_data.py で生成（Swiss Ephemeris の計算値）
window.CHARTS = {
 "nm": {
  "label": "新月 2026/10/11 00:50 JST 東京",
  "bodies": {
   "sun": {
    "lon": 197.360606,
    "retro": false
   },
   "moon": {
    "lon": 197.359639,
    "retro": false
   },
   "mercury": {
    "lon": 222.31117,
    "retro": false
   },
   "venus": {
    "lon": 217.42347,
    "retro": true
   },
   "mars": {
    "lon": 127.220651,
    "retro": false
   },
   "jupiter": {
    "lon": 141.251596,
    "retro": false
   },
   "saturn": {
    "lon": 10.820439,
    "retro": true
   },
   "uranus": {
    "lon": 65.329255,
    "retro": true
   },
   "neptune": {
    "lon": 2.599152,
    "retro": true
   },
   "pluto": {
    "lon": 303.075652,
    "retro": true
   },
   "asc": {
    "lon": 135.996882,
    "retro": false
   },
   "mc": {
    "lon": 38.919471,
    "retro": false
   }
  },
  "cusps": [
   135.996882,
   158.905571,
   186.446746,
   218.919471,
   253.667052,
   286.618838,
   315.996882,
   338.905571,
   6.446746,
   38.919471,
   73.667052,
   106.618838
  ]
 },
 "fm": {
  "label": "満月 2026/9/27 01:49 JST 東京",
  "bodies": {
   "sun": {
    "lon": 183.619739,
    "retro": false
   },
   "moon": {
    "lon": 3.619577,
    "retro": false
   },
   "mercury": {
    "lon": 204.80182,
    "retro": false
   },
   "venus": {
    "lon": 217.680037,
    "retro": false
   },
   "mars": {
    "lon": 119.164608,
    "retro": false
   },
   "jupiter": {
    "lon": 138.808948,
    "retro": false
   },
   "saturn": {
    "lon": 11.913308,
    "retro": true
   },
   "uranus": {
    "lon": 65.590304,
    "retro": true
   },
   "neptune": {
    "lon": 2.981014,
    "retro": true
   },
   "pluto": {
    "lon": 303.156433,
    "retro": true
   },
   "asc": {
    "lon": 136.802966,
    "retro": false
   },
   "mc": {
    "lon": 39.931105,
    "retro": false
   }
  },
  "cusps": [
   136.802966,
   159.790317,
   187.423921,
   219.931105,
   254.620108,
   287.483579,
   316.802966,
   339.790317,
   7.423921,
   39.931105,
   74.620108,
   107.483579
  ]
 },
 "nmLondon": {
  "label": "新月と同じ瞬間 ロンドン",
  "bodies": {
   "sun": {
    "lon": 197.360606,
    "retro": false
   },
   "moon": {
    "lon": 197.359639,
    "retro": false
   },
   "mercury": {
    "lon": 222.31117,
    "retro": false
   },
   "venus": {
    "lon": 217.42347,
    "retro": true
   },
   "mars": {
    "lon": 127.220651,
    "retro": false
   },
   "jupiter": {
    "lon": 141.251596,
    "retro": false
   },
   "saturn": {
    "lon": 10.820439,
    "retro": true
   },
   "uranus": {
    "lon": 65.329255,
    "retro": true
   },
   "neptune": {
    "lon": 2.599152,
    "retro": true
   },
   "pluto": {
    "lon": 303.075652,
    "retro": true
   },
   "asc": {
    "lon": 329.540115,
    "retro": false
   },
   "mc": {
    "lon": 257.715766,
    "retro": false
   }
  },
  "cusps": [
   329.540115,
   27.779642,
   57.815534,
   77.715766,
   95.234032,
   115.383824,
   149.540115,
   207.779642,
   237.815534,
   257.715766,
   275.234032,
   295.383824
  ]
 }
};
window.CHART = window.CHARTS.nm;
