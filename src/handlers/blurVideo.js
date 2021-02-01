'use strict';
const { spawn } = require('child_process');
const util = require('util');
const fs = require('fs-extra');

// eslint-disable-next-line import/order
const exec = util.promisify(require('child_process').exec);
const logOutput = name => data => console.log(`[${name}] ${data}`);

function run(videoData) {
  return new Promise((resolve, reject) => {
    const process = spawn('python', ['./src/handlers/blur_video.py', JSON.stringify(videoData)]);

    const out = [];
    process.stdout.on('data', data => {
      out.push(data.toString());
      logOutput('stdout')(data);
    });

    const err = [];
    process.stderr.on('data', data => {
      err.push(data.toString());
      logOutput('stderr')(data);
    });

    process.on('exit', (code, signal) => {
      logOutput('exit')(`${code} (${signal})`);
      if (code === 0) {
        resolve(out);
      } else {
        reject(new Error(err.join('\n')));
      }
    });
  });
}

module.exports = async (input, videoData) => {
  console.log('Initializing temporary files');
  if (!fs.existsSync('./temp')) await fs.mkdir('./temp');
  if (fs.existsSync(`./temp/${videoData.id}`)) await fs.remove(`./temp/${videoData.id}`);
  await fs.mkdir(`./temp/${videoData.id}`);
  await fs.mkdir(`./temp/${videoData.id}/raw-frames`);
  await fs.mkdir(`./temp/${videoData.id}/edited-frames`);

  console.log('Decoding');
  await exec(`ffmpeg -hwaccel cuda -i ${input} -vf fps=30 temp/${videoData.id}/raw-frames/%d.png`, { shell: true });

  try {
    console.log('Rendering');
    const output = await run(videoData);
    logOutput('main')(output);

    console.log('Encoding');
    await exec(
      // eslint-disable-next-line max-len
      `ffmpeg -hwaccel cuda -r 30 -i temp/${videoData.id}/edited-frames/%d.png -c:v libx264 -vf fps=30 -pix_fmt yuv420p temp/${videoData.id}/no-audio.mp4`,
      { shell: true },
    );

    console.log('Adding audio');
    await exec(
      `ffmpeg -i temp/${videoData.id}/no-audio.mp4 -i ${input} -c copy -map 0:v:0 -map 1:a:0 output/${Date.now()}.mp4`,
      { shell: true },
    );

    console.log('Cleaning up');
    await fs.remove(`temp/${videoData.id}`);
  } catch (e) {
    console.error('Error during script execution ', e.stack);
    process.exit(1);
  }
};
