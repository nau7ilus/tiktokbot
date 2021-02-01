'use strict';

const TikTokScraper = require('tiktok-scraper');
const blurVideo = require('./handlers/blurVideo');

(async () => {
  try {
    const posts = await TikTokScraper.hashtag('overwhelmed', {
      number: 1,
      download: true,
    });

    for (const video of posts.collector) {
      if (!video.downloaded) continue;
      const { id, authorMeta, diggCount, shareCount, commentCount } = video;
      const { name, nickName, avatar, verified } = authorMeta;

      blurVideo(`#overwhelmed/${id}.mp4`, {
        id,
        diggCount,
        shareCount,
        commentCount,
        author: { name, nickName, avatar, verified },
      });
    }
  } catch (error) {
    console.log(error);
  }
})();
