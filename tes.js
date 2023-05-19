const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const axios = require('axios');
const fs = require('fs');
const readline = require('readline');

puppeteer.use(StealthPlugin());

async function getRandomUser() {
  try {
    const response = await axios.get('https://randomuser.me/api/?nat=us');
    return response.data.results[0];
  } catch (error) {
    console.error('Error fetching random user:', error);
  }
}

function getRandomNumber(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}

async function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

rl.question('Masukkan domain yang terhubung di generator.email: ', async (domain) => {
  rl.question('Masukkan password yang diinginkan: ', async (password) => {
    rl.question('Berapa akun yang mau dibuat?\n ', async (count) => {
      rl.close();

      for (let i = 0; i < parseInt(count); i++) {
        try {
          const randomUser = await getRandomUser();
          const firstName = randomUser.name.first;
          const lastName = randomUser.name.last;
          const randomNumber = getRandomNumber(1, 9999);
          const email = `${firstName}${lastName}${randomNumber}@${domain}`.toLowerCase();
          const emailParts = email.split('@');
          const nickname = emailParts[0];

          const browser = await puppeteer.launch({
            headless: false,
            args: ['--enable-javascript', '--disable-web-security'],
          });

          const page = await browser.newPage();
          await page.setViewport({ width: 1200, height: 800 });

          await page.goto('https://www.webtoons.com/member/join?loginType=EMAIL', { waitUntil: 'networkidle2', timeout: 60000 });

          await page.waitForSelector('#email');

          console.log('Sedang menginput email...');
          await page.type('#email', email);
          await delay(2500);

          console.log('Sedang menginput password...');
          await page.type('#pw', password);
          await delay(2500);

          console.log('Sedang menginput repeat password...');
          await page.type('#retype_pw', password);
          await delay(2500);

          console.log('Sedang menginput nickname...');
          await page.type('#nickname', nickname);
          await delay(2500);

          await page.click('#content > div > div.inner_wrap > div > a');
          await delay(5000);

          // Open the generator email
          await page.goto(`https://generator.email/${email}`, { waitUntil: 'networkidle0', timeout: 60000 });

          try {
            let link = await page.waitForSelector('a[href*="emailVerification"]', { timeout: 60000 });
            let confirmUrl = await page.evaluate(el => el.href, link);

            if (confirmUrl) {
              const confirmPage = await browser.newPage();
              await confirmPage.goto(confirmUrl, { waitUntil: 'networkidle0', timeout: 60000 });
              await confirmPage.waitForTimeout(5000);
              await confirmPage.close();

              fs.appendFile('akun.txt', `${email}|${password}\n`, (err) => {
                if (err) throw err;
                console.log(`[${i + 1}] verifikasi berhasil \x1b[32m${email}\x1b[0m , save to akun.txt\n`);
              });
            } else {
              console.error('Could not find confirmation URL');
            }
          } catch (error) {
            console.error('Error waiting for verification link:', error);
          }

          await browser.close();
          await delay(2500);
        } catch (error) {
          console.error('Error processing account:', error);
        }
      }
    });
  });
});
