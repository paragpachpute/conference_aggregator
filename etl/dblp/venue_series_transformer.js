function (data) {
  const rawVenue = data.content.dblp;
  const invitationType = 'Conference';


  /**
  * This function converts the DBLP key into OR specific id.
  * example: db/conf/haptics/index => .HAPTICS/Conference
  * @param {string} key - string that identifies a venue uniquely in DBLP
  * @return {string} - converted _id field as per OR's conventions
  */
  function getIdFromKey(key, invitationType) {
    return `.${key.split('/').slice(2, -1).join('/').toUpperCase()}/${invitationType}`;
  }

  const venue = {};
  venue.id = getIdFromKey(rawVenue.dblp_key, invitationType);
  venue.invitation = `Venue/-/${invitationType}`;
  venue.readers = ['everyone'];
  venue.nonreaders = [];
  venue.writers = ['dblp.org'];

  venue.content = {};
  venue.content.name = rawVenue.name;
  venue.content.noteline = rawVenue.noteline;
  venue.content.external_links = rawVenue.external_links;

  return venue;
};