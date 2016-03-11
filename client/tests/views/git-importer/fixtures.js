function gitImporterFixtures(name) {
  switch (name) {
    case 'state':
      return {
        locales: [{
          name: 'en_ZA'
        }, {
          name: 'zu_ZA'
        }]
      };
    case 'props':
      return gitImporterFixtures('state');
  }
}


export default gitImporterFixtures;
