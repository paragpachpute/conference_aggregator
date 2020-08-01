function (data) {
  const rawVenue = data.content.dblp;
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
               'November', 'December'];
  const dayRegEx = /[1-9][0-9]?/g;
  const yearRegEx = /([1-3][0-9]{3})/;
  const dblpBaseUrl = 'https://dblp.org/';
  const dblpConfBaseUrl = `${dblpBaseUrl}db/`;
  const invitationTypeConference = 'Conference';
  const invitationTypeWorkshop = 'Workshop';

  /**
  * This function converts the DBLP key into OR specific id.
  * example: conf/akbc/2019 => .AKBC/2019/Conference
  * @param {string} key - string that identifies a venue uniquely in DBLP
  * @return {string} - converted _id field as per OR's conventions
  */
  function getIdFromKey(key, invitationType) {
    return `.${key.split('/').slice(1).join('/').toUpperCase()}/${invitationType}`;
  }

  /**
  * This function converts the DBLP key into OR specific id of the parent venue.
  * example: conf/akbc/2019 => .AKBC/Conference
  * @param {string} key - string that identifies a venue uniquely in DBLP
  * @return {string} - converted parent _id field as per OR's conventions
  */
  function getParentIdFromKey(key, invitationType) {
    return `.${key.split('/').slice(1, -1).join('/').toUpperCase()}/${invitationType}`;
  }

  /**
  * This function extracts parents for the given venue
  * example: conf/akbc/2019 => .AKBC/Conference and .NIPS/2017/Conference
  * @param {string} proceedingKey - identifies a venue uniquely in DBLP
  * @param {string} invitationType - specifies if its a workshop or a conference
  * @param {string} parentLink - url to the parent conference in DBLP
  * @param {string} year - year in which that workshop/conference was held
  * @return {list} - parents for the given venue
  */
  function getParents(proceedingKey, invitationType, parentLink, year) {
    const parents = [];
    parents.push(`.${proceedingKey.split('/').slice(1, -1).join('/').toUpperCase()}/${invitationType}`);

    if (parentLink && parentLink.includes(dblpConfBaseUrl)) {
      // Mapping 'https://dblp.org/db/conf/nips/index.html' => '.NIPS/2017'
      let parent = parentLink.split(dblpConfBaseUrl)[1]; // => conf/nips/index.html
      parent = parent.split('/').slice(0, -1).join('/');  // => conf/nips
      parent += `/${year}`;  // => conf/nips/2017
      parents.push(getIdFromKey(parent, invitationTypeConference));
    }
    return parents;
  }

  /**
  * Given string of the form 'March 13-17,2010' get start and end timestamps
  * @param {string} dateStr - string representing the date range
  * @return {[int, int]} - start and end timestamps
  **/
  function getTimestampsFromDateString(dateStr) {
    let startDate;
    let endDate;

    for (i in months) {
      if (dateStr.includes(months[i])) {
        let startMonth = i;
        let endMonth = i;

        let startYear = dateStr.match(yearRegEx)[0];
        let endYear = startYear;

        let startDay;
        let endDay;

        dateStr = dateStr.replace(startYear, '');
        if (dateStr.includes('-')) {
          if (dateStr.split('-')[0].match(dayRegEx)) {
            startDay = dateStr.split('-')[0].match(dayRegEx).slice(-1);
          } else {
            startDay = 1;
          }

          if (dateStr.split('-')[1].match(dayRegEx)) {
            endDay = dateStr.split('-')[1].match(dayRegEx)[0];

            // Handeling case for date like October 29 - November 02,2018
            if (endDay < startDay) {
              if (startMonth < 12) {
                endMonth++;
              } else {
                endYear++;
                endMonth = 0;
              }
            }
          } else {
            endDay = startDay;
          }
          // YYYY, MM, DD
          startDate = new Date(parseInt(startYear, 10), parseInt(startMonth, 10), parseInt(startDay, 10));

          try {
            endDate = new Date(parseInt(endYear, 10), parseInt(endMonth, 10), parseInt(endDay, 10));
          } catch (e) {
            endDate = startDate;
          }
        } else {
          if (dateStr.match(dayRegEx)) {
            startDay = dateStr.match(dayRegEx).slice(-1);
            startDate = new Date(parseInt(startYear, 10), parseInt(startMonth, 10), parseInt(startDay, 10));
          } else {
            startDate = new Date(parseInt(startYear, 10), parseInt(startMonth, 10));
          }
          endDate = startDate;
        }
        break;
      }
    }

    if (!startDate || !endDate) {
      return [null, null];
    }

    return [startDate.getTime(), endDate.getTime()];
  }

  /**
  * Extracts date range from a string.
  * Example: extracts 'September 28-30, 2015' from '10th EAI International Conference on Body Area Networks, BODYNETS 2015, Sydney, Australia, September 28-30, 2015'
  * @param {string} titleString - string to extract date from
  * @param {string} year - fallback year, if the titleString does not contain year
  */
  function getDateFromString(titleString, year) {
    for (let month of months) {
      let tokens = titleString.split(',');
      for (let t in tokens) {
        if (tokens[t].includes(month)) {
          t = parseInt(t, 10);
          let date = tokens[t];
          if (t+1 < tokens.length && tokens[t+1].match(yearRegEx)) {
            let parsedYear = tokens[t+1].match(yearRegEx)[0];
            date += `,${parsedYear}`;
          } else if (!date.match(yearRegEx)) {
            // year is not present in the date, add it from the tag fetched separately
            date += `,${year}`;
          }
          return date.trim();
        }
      }
    }
  }

  // Transformation starts from here


  let invitationType;
  if (rawVenue.title.toLowerCase().includes('workshop')) {
    invitationType = invitationTypeWorkshop;
  } else {
    invitationType = invitationTypeConference;
  }

  let seriesName = rawVenue.proceeding_key.split('/').slice(1, -1).join('/');

  let confDateStr = getDateFromString(rawVenue.title, rawVenue.year);
  let startDate = null;
  let endDate = null;
  if (confDateStr) {
    let timestamps = getTimestampsFromDateString(confDateStr);
    startDate = timestamps[0];
    endDate = timestamps[1];
  }

  let dblpUrl;
  if (rawVenue.dblp_url) {
    dblpUrl = dblpBaseUrl + rawVenue.dblp_url;
  }

  const venue = {};
  venue.id = getIdFromKey(rawVenue.proceeding_key, invitationType);
  venue.invitation = `Venue/-/${invitationType}/Occurrence`;
  venue.readers = ['everyone'];
  venue.nonreaders = [];
  venue.writers = ['dblp.org'];

  venue.content = {};
  venue.content.name = rawVenue.title.split(',').slice(0, 2).join(',');
  venue.content.location = rawVenue.location;
  venue.content.year = rawVenue.year;
  venue.content.parents = getParents(rawVenue.proceeding_key, invitationType, rawVenue.parent_link, rawVenue.year);
  venue.content.program_chairs = rawVenue.editors_with_links;
  venue.content.publisher = rawVenue.publisher;
  venue.content.html = rawVenue.ee;
  venue.content.shortname = rawVenue.booktitle;
  venue.content.dblp_url = dblpUrl;
  venue.content.startdate = startDate;
  venue.content.enddate = endDate;

  return venue;
};