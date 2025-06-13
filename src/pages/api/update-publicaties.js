import Parser from 'rss-parser';
import fs from 'fs';

const parser = new Parser();
const allItems = [];

// 👉 Hulpfunctie: zet naar ISO-formaat
function toISODate(d) {
  if (typeof d !== 'string') return '';
  const parsed = new Date(d);
  if (isNaN(parsed)) return '';
  return parsed.toISOString().split('T')[0];
}

const feeds = [
  {
    url: 'https://www.stibbe.com/publications-insights/all/all/all/all/all/all/all/285,286/rss.xml',
    bron: 'Stibbe',
    type: 'Blog',
    parseItem: (item) => {
  let rawDatum = '';

  if (typeof item.pubDate === 'string') {
    rawDatum = item.pubDate;
  } else if (item.pubDate?.time?.[0]?._) {
    rawDatum = item.pubDate.time[0]._;
  }

  return {
    titel: item.title ?? '',
    url: item.link ?? '',
    auteur: item.creator || item.author || 'Stibbe',
    datum: toISODate(rawDatum),
    bron: 'Stibbe',
    type: 'Blog',
    thema: '',
    samenvatting: item.contentSnippet || item.content || '',
  };
},
  {
    url: 'https://vng.nl/rss/publicaties.xml',
    bron: 'VNG',
    type: 'Publicatie',
    parseItem: (item) => {
      const rawTitle = item.title ?? '';
      const title = rawTitle.toLowerCase();
      const content = (item.content ?? '').toLowerCase();

      const keywords = {
        'factsheet': 'Factsheet',
        'handreiking': 'Handreiking',
        'position paper': 'Position paper',
        'podcast': 'Podcast',
        'presentatie': 'Presentatie',
        'rapport': 'Rapport',
      };

      let type = 'Overig';
      for (const keyword in keywords) {
        if (title.includes(keyword) || content.includes(keyword)) {
          type = keywords[keyword];
          break;
        }
      }

      return {
        titel: rawTitle,
        url: item.link ?? '',
        auteur: '',
        datum: toISODate(item.pubDate),
        bron: 'VNG',
        type,
        thema: '',
        samenvatting: item.contentSnippet || item.content || item.summary || '',
      };
    },
  },
];

// 1. Verzamel alle items
for (const feed of feeds) {
  try {
    const parsedFeed = await parser.parseURL(feed.url);
    const items = parsedFeed.items.map(feed.parseItem);
    allItems.push(...items);
  } catch (err) {
    console.error(`Fout bij ophalen van ${feed.url}:`, err);
  }
}

// 2. Sorteer alles op ISO-datum (nieuwste eerst)
allItems.sort((a, b) => new Date(b.datum) - new Date(a.datum));

// 3. Filter en combineer
const stibbeItems = allItems.filter(item => item.bron === 'Stibbe');
const andereItems = allItems.filter(item => item.bron !== 'Stibbe' && item.type !== 'Overig');
const beperktAndere = andereItems.slice(0, 50);
const alles = [...stibbeItems, ...beperktAndere];

// 4. Schrijf weg
fs.writeFileSync('../../../public/content/stibbe.json', JSON.stringify(stibbeItems, null, 2));
console.log(`✅ Aantal Stibbe-publicaties opgeslagen: ${stibbeItems.length}`);
