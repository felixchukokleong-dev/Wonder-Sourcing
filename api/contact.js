/**
 * Serverless contact form handler for Wonder Sourcing.
 *
 * Receives POST submissions from /contact.html (JSON body), injects the Web3Forms
 * access key server-side (from Vercel Environment Variable WEB3FORMS_ACCESS_KEY),
 * and forwards the payload to Web3Forms so the key never reaches the browser.
 *
 * Required Vercel Environment Variable:
 *   WEB3FORMS_ACCESS_KEY  -> your Web3Forms access key
 */
export default async function handler(request, response) {
  // Only allow POST
  if (request.method !== 'POST') {
    return response.status(405).json({ success: false, message: 'Method not allowed' });
  }

  const accessKey = process.env.WEB3FORMS_ACCESS_KEY;

  if (!accessKey) {
    console.error('WEB3FORMS_ACCESS_KEY is not configured');
    return response.status(500).json({
      success: false,
      message: 'Server configuration error',
    });
  }

  try {
    // Parse JSON body from the client
    let body;
    try {
      body = await request.json();
    } catch (e) {
      return response.status(400).json({
        success: false,
        message: 'Invalid request body',
      });
    }

    // Build FormData to forward to Web3Forms, injecting the access key
    const formData = new FormData();
    formData.append('access_key', accessKey);

    // Copy all fields from the request body, except access_key if the client sent one
    if (body && typeof body === 'object') {
      for (const [key, value] of Object.entries(body)) {
        if (key !== 'access_key' && value !== undefined && value !== null) {
          formData.append(key, String(value));
        }
      }
    }

    const web3Res = await fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      body: formData,
    });

    const result = await web3Res.json();

    if (!web3Res.ok || result.success === false) {
      console.error('Web3Forms submission failed:', result);
      return response.status(web3Res.status || 500).json({
        success: false,
        message: result.message || 'Submission rejected',
      });
    }

    return response.status(200).json({
      success: true,
      message: 'Submission received',
    });
  } catch (error) {
    console.error('Contact form handler error:', error);
    return response.status(500).json({
      success: false,
      message: 'Unexpected server error',
    });
  }
}
