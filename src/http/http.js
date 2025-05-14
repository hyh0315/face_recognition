/**
 * @file Simplify fetch usage
 * @author ty
 */

/**
 * A http module like go net/http
 */
export class Http {
  /** A simple http client with timeout. */
  static Client = class {
    /**
     * @param {number|null} timeout 
     */
    constructor(timeout = null) {
      this.#timeout = timeout;
    }
    /**
     * @param {string} url 
     * @returns {Promise<Response>}
     */
    get(url) {
      const request = new Http.Request(url);
      return this.do(request);
    }

    /**
     * Post method, using json body. 
     * @param {string} url 
     * @param {object} body 
     * @returns {Promise<Response>}
     */
    post(url, body) {
      const request = new Http.Request(url, 'POST', {
        'Content-Type': 'application/json'
      }, JSON.stringify(body));
      return this.do(request);
    }

    /**
     * using custom request
     * @param {Http.Request} request 
     * @returns {Promise<Response>}
     */
    do(request) {
      if (this.#timeout) {
        return Promise.race([
          this.#send(request),
          new Promise((_, reject) => {
            setTimeout(() => reject('request timeout'), this.#timeout);
          }),
        ]);
      }
      return this.#send(request);
    }

    #timeout
    #send(request) {
      const {url, method, headers, body} = request;
      return fetch(url, {
        method,
        headers,
        body,
      });
    }
  }
  
  static Request = class {
    url
    method
    headers
    body
    constructor(url, method = 'GET', headers = {}, body = null) {
      this.url = url;
      this.method = method;
      this.headers = headers;
      this.body = body;
    }
  }
}