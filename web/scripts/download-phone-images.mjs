import { mkdir, writeFile } from 'node:fs/promises';

// Keep product photography local so catalogue animations do not rely on hotlinks.
const products = [
  ['iphone-13-128', 'apple/apple-iphone-13', 'https://www.gsmarena.com/apple_iphone_13-pictures-11103.php'],
  ['samsung-a55-128', 'samsung/samsung-galaxy-a55', 'https://www.gsmarena.com/samsung_galaxy_a55-pictures-12824.php'],
  ['xiaomi-note13-256', 'xiaomi/xiaomi-redmi-note-13-5g', 'https://www.gsmarena.com/xiaomi_redmi_note_13-pictures-12776.php'],
  ['poco-x6-256', 'xiaomi/xiaomi-poco-x6', 'https://www.gsmarena.com/xiaomi_poco_x6-pictures-12723.php'],
  ['pixel-8a-128', 'google/google-pixel-8a', 'https://www.gsmarena.com/google_pixel_8a-pictures-12937.php'],
];
await mkdir('public/phones', { recursive: true });
for (const [id, path, source] of products) {
  const html = await (await fetch(source)).text();
  const urls = [...new Set(html.match(/https:\/\/fdn2?\.gsmarena\.com\/vv\/pics\/[^"\s<>]+\.jpg/g) ?? [])].slice(0, 4);
  console.log(id, urls);
  for (const [offset, url] of urls.entries()) {
    const index = offset + 1;
    const response = await fetch(url);
    if (!response.ok) { console.log(`${id}/${index}: ${response.status}`); continue; }
    await writeFile(`public/phones/${id}-${index}.jpg`, Buffer.from(await response.arrayBuffer()));
    console.log(`${id}/${index}: saved`);
  }
}
await writeFile('public/phones/SOURCES.md', '# Product photography\n\nImages are product photographs supplied through GSMArena galleries. All product marks belong to their respective owners.\n\n' + products.map(([id, , source]) => `- ${id}: ${source}`).join('\n') + '\n');
