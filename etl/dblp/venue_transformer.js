function (data) {
  let raw_venue = data.content.dblp;
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
               'November', 'December'];
  const dayRegEx = /[1-9][0-9]?/g;
  const yearRegEx = /([1-3][0-9]{3})/;
  const dblp_base_url = 'https://dblp.org/';
  const dblp_conf_base_url = `${dblp_base_url}db/`;
  const invitation_type_conference = 'Conference';
  const invitation_type_workshop = 'Workshop';

  /**
  * This function converts the DBLP key into OR specific id.
  * example: conf/akbc/2019 => .AKBC/2019/Conference
  * @param {string} key - string that identifies a venue uniquely in DBLP
  * @return {string} - converted _id field as per OR's conventions
  */
  function get_id_from_key(key, invitation_type) {
    return `.${key.split('/').slice(1).join('/').toUpperCase()}/${invitation_type}`;
  }

  /**
  * This function converts the DBLP key into OR specific id of the parent venue.
  * example: conf/akbc/2019 => .AKBC/Conference
  * @param {string} key - string that identifies a venue uniquely in DBLP
  * @return {string} - converted parent _id field as per OR's conventions
  */
  function get_parent_id_from_key(key, invitation_type) {
    return `.${key.split('/').slice(1, -1).join('/').toUpperCase()}/${invitation_type}`;
  }

  /**
  * This function extracts parents for the given venue
  * example: conf/akbc/2019 => .AKBC/Conference and .NIPS/2017/Conference
  * @param {string} proceeding_key - identifies a venue uniquely in DBLP
  * @param {string} invitation_type - specifies if its a workshop or a conference
  * @param {string} parent_link - url to the parent conference in DBLP
  * @param {string} year - year in which that workshop/conference was held
  * @return {list} - parents for the given venue
  */
  function get_parents(proceeding_key, invitation_type, parent_link, year) {
    let parents = [];
    parents.push(`.${proceeding_key.split('/').slice(1, -1).join('/').toUpperCase()}/${invitation_type}`);

    if (parent_link != null && parent_link.includes(dblp_conf_base_url)) {
      // Mapping 'https://dblp.org/db/conf/nips/index.html' => '.NIPS/2017'
      parent = parent_link.split(dblp_conf_base_url)[1]; // => conf/nips/index.html
      parent = parent.split('/').slice(0, -1).join('/');  // => conf/nips
      parent += `/${year}`;  // => conf/nips/2017
      parents.push(get_id_from_key(parent, invitation_type_conference));
    }
    return parents;
  }

  /**
  * Given string of the form 'March 13-17,2010' get start and end timestamps
  * @param {string} date_str - string representing the date range
  * @return {[int, int]} - start and end timestamps
  **/
  function get_timestamps_from_date_string(date_str) {
    start_date = null;
    end_date = null;

    for (i in months) {
      if (date_str.includes(months[i])) {
        year = date_str.match(yearRegEx)[0];
        date_str = date_str.replace(year, '');
        if (date_str.includes('-')) {
          if (date_str.split('-')[0].match(dayRegEx)) {
            start_day = date_str.split('-')[0].match(dayRegEx).slice(-1);
          } else {
            start_day = 1;
          }

          if (date_str.split('-')[1].match(dayRegEx)) {
            end_day = date_str.split('-')[1].match(dayRegEx)[0];
          } else {
            end_day = start_day;
          }
          // YYYY, MM, DD
          start_date = new Date(parseInt(year, 10), parseInt(i, 10), parseInt(start_day, 10));

          try {
            end_date = new Date(parseInt(year), parseInt(i), parseInt(end_day));
          } catch (e) {
            end_date = start_date;
          }
        } else {
          if (date_str.match(dayRegEx)) {
            start_day = date_str.match(dayRegEx).slice(-1);
            start_date = new Date(parseInt(year), parseInt(i), parseInt(start_day));
          } else {
            start_date = new Date(parseInt(year), parseInt(i)).getTime();
          }
          end_date = start_date;
        }
      }
    }

    if (!start_date || !end_date) {
      return [null, null];
    }
    return [start_date.getTime(), end_date.getTime()];
  }

  /**
  * Extracts date range from a string.
  * Example: extracts 'September 28-30, 2015' from '10th EAI International Conference on Body Area Networks, BODYNETS 2015, Sydney, Australia, September 28-30, 2015'
  * @param {string} title_string - string to extract date from
  * @param {string} year - fallback year, if the title_string does not contain year
  */
  function get_date_from_string(title_string, year) {
    for (month of months) {
      tokens = title_string.split(',');
      for (t in tokens) {
        t = parseInt(t);
        if (tokens[t].includes(month)) {
          date = tokens[t];
          if (t+1 < tokens.length && tokens[t+1].match()) {
            parsedYear = tokens[t+1].match(yearRegEx)[0];
            date += `,${parsedYear}`;
          } else if (date.match(yearRegEx) == null) {
            // year is not present in the date, add it from the tag fetched separately
            date += `,${year}`;
          }
          return date.trim();
        }
      }
    }
  }

  // Transformation starts from here


  let invitation_type = null
  if (raw_venue.title.toLowerCase().includes('workshop')) {
    invitation_type = invitation_type_workshop;
  } else {
    invitation_type = invitation_type_conference;
  }

  let series_name = raw_venue.proceeding_key.split('/').slice(1, -1).join('/');
  
  let conf_date_str = get_date_from_string(raw_venue.title, raw_venue.year);
  let start_date = null;
  let end_date = null;
  if (conf_date_str) {
    let timestamps = get_timestamps_from_date_string(conf_date_str);
    start_date = timestamps[0];
    end_date = timestamps[1];
  }
  
  let dblp_url = null;
  if (raw_venue.dblp_url) {
    dblp_url = dblp_base_url + raw_venue.dblp_url;
  }

  let venue = {};
  venue.venueid = get_id_from_key(raw_venue.proceeding_key, invitation_type);
  venue.invitation = `Venue/-/${invitation_type}/Occurrence`;
  venue.readers = ['everyone'];
  venue.nonreaders = [];
  venue.writers = ['dblp.org'];
  
  venue.content = {};
  venue.content.name = raw_venue.title.split(',').slice(0, 2).join(',');
  venue.content.location = raw_venue.location;
  venue.content.year = raw_venue.year;
  venue.content.parents = get_parents(raw_venue.proceeding_key, invitation_type, raw_venue.parent_link, raw_venue.year);
  venue.content.program_chairs = raw_venue.editors_with_links;
  venue.content.publisher = raw_venue.publisher;
  venue.content.html = raw_venue.ee;
  venue.content.shortname = raw_venue.booktitle;
  venue.content.dblp_url = dblp_url;
  venue.content.start_date = start_date;
  venue.content.end_date = end_date;
  
  return venue;
};