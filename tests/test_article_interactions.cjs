/* Native range controls clamp assigned values to their current bounds. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const { chromium } = require('playwright');

test('the attribution explorer selects the first rebound session on initial load and episode changes', async () => {
  const root = path.resolve(__dirname, '..');
  const browser = await chromium.launch({
    headless: true,
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
  });
  try {
    const page = await browser.newPage();
    const data = JSON.parse(fs.readFileSync(path.join(root, 'assets/portfolio-attribution/dynamics.json'), 'utf8'));
    const markup = fs.readFileSync(path.join(root, '_includes/attribution-dynamics.html'), 'utf8')
      .replace(/<link[^>]*>|<script[^>]*><\/script>/g, '');
    await page.setContent(markup);
    // A browser can restore the first episode before the explorer initializes.
    await page.evaluate((data) => {
      document.querySelector('.ad-episode').value = '0';
      window.fetch = async () => ({ ok: true, json: async () => data });
    }, data);
    await page.addScriptTag({ path: path.join(root, 'assets/js/attribution-dynamics.js') });
    await page.waitForFunction(() => document.querySelector('.ad-selected-date').textContent.length > 0);
    for (const [step, episodeIndex] of [0, 1, 0].entries()) {
      if (step > 0) await page.selectOption('.ad-episode', String(episodeIndex));
      const episode = data.episodes[episodeIndex];
      const expected = episode.factors.volatility.findIndex(row => row[0] > episode.low);
      assert.equal(Number(await page.locator('.ad-slider').inputValue()), expected);
      assert.equal(Number(await page.locator('.ad-slider').getAttribute('max')), episode.factors.volatility.length - 1);
    }
  } finally {
    await browser.close();
  }
});
