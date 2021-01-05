'use strict';

const TikTokScraper = require('tiktok-scraper');

const options = {
  number: 1,
  download: true,
  sessionList: ['sid_tt=asdasd13123123123adasda;'],
};

const getVideosByMusic = async url => {
  const musicInfo = await TikTokScraper.getMusicInfo(url);
  const musicID = musicInfo.music.id;

  const videosData = await TikTokScraper.music(musicID, options);

  return videosData;
};

const getVideosByHashtag = hashtag => TikTokScraper.music(hashtag, options);

module.exports = { getVideosByMusic, getVideosByHashtag };
