"use strict";

export const _fetchText = function (url) {
  return function (onOk) {
    return function (onErr) {
      return function () {
        fetch(url)
          .then(function (response) {
            if (!response.ok) {
              throw new Error("HTTP " + response.status + " " + response.statusText);
            }
            return response.text();
          })
          .then(function (body) {
            return onOk(body)();
          })
          .catch(function (e) {
            var msg = e && typeof e.message === "string" ? e.message : String(e);
            return onErr(msg)();
          });
        return {};
      };
    };
  };
};

export const setBodyHtml = function (html) {
  return function () {
    document.body.innerHTML = html;
    return {};
  };
};

