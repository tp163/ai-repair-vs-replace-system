type PhonePhoto = {
  file: string;
  view: string;
  creator: string;
  source: string;
  license: string;
  licenseUrl: string;
};

const commons = 'https://commons.wikimedia.org/wiki/File:';
const shareAlike = { license: 'CC BY-SA 4.0', licenseUrl: 'https://creativecommons.org/licenses/by-sa/4.0/' };
const unsplash = { license: 'Unsplash License', licenseUrl: 'https://unsplash.com/license' };

export const phonePhotos: Record<string, PhonePhoto[]> = {
  'Apple iPhone 13': [
    {
      file: 'iphone-colors',
      view: 'Color lineup',
      creator: 'Daniel Romero',
      source: 'https://unsplash.com/photos/four-different-colored-iphones-sitting-on-a-table-JSQva3za368',
      ...unsplash,
    },
    {
      file: 'iphone-front',
      view: 'Front illustration',
      creator: 'Rafael Fernandez',
      source: commons + 'IPhone_13_vector.svg',
      ...shareAlike,
    },
    {
      file: 'iphone-camera',
      view: 'Camera close-up',
      creator: 'Fujiphilm',
      source: 'https://unsplash.com/photos/a-close-up-of-the-back-of-an-iphone-ZY5cwEDWkEU',
      ...unsplash,
    },
  ],
  'Samsung Galaxy A55': [
    {
      file: 'galaxy-front',
      view: 'Front',
      creator: 'Captainmorlypogi1959',
      source: commons + 'Samsung_Galaxy_A55_5G_2024.jpg',
      ...shareAlike,
    },
  ],
  'Google Pixel 8a': [
    {
      file: 'pixel-front',
      view: 'Front',
      creator: 'Miyako Fujimiya',
      source: commons + 'Pixel_8a.jpg',
      license: 'CC BY 4.0',
      licenseUrl: 'https://creativecommons.org/licenses/by/4.0/',
    },
  ],
};
