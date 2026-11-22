import unittest
import app
from src.nearby_sources import find_nearby_pollutant_sources, get_nearby_sources_for_city, CITY_CENTERS
from src.realtime_api import fetch_live_air_quality

class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        with self.client.session_transaction() as sess:
            sess['is_authenticated'] = True
            sess['is_admin'] = True
            sess['username'] = 'admin'

    def test_home_page(self):
        unauth_client = app.app.test_client()
        # Unauthenticated redirects to /login
        res_unauth = unauth_client.get('/')
        self.assertEqual(res_unauth.status_code, 302)
        self.assertIn('/login', res_unauth.headers.get('Location', ''))

        # Login page renders 200
        res_login = unauth_client.get('/login')
        self.assertEqual(res_login.status_code, 200)
        self.assertIn('AeroIntel Access Gateway', res_login.text)

        # Authenticated loads dashboard with 200
        res_auth = self.client.get('/')
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn('AeroIntel', res_auth.text)

    def test_cities_endpoint(self):
        res = self.client.get('/api/cities')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Delhi', res.json['cities'])

    def test_presets_endpoint(self):
        res = self.client.get('/api/presets')
        self.assertEqual(res.status_code, 200)
        presets = res.json['presets']
        self.assertEqual(len(presets), 5)
        cities = {p['city'] for p in presets}
        self.assertTrue({'Bengaluru', 'Hyderabad', 'Mumbai', 'Kolkata', 'Delhi'}.issubset(cities))

    def test_nearby_sources_delhi(self):
        res = self.client.get('/api/nearby-sources?city=Delhi')
        self.assertEqual(res.status_code, 200)
        data = res.json['data']
        self.assertGreater(data['total_hotspots_found'], 0)
        self.assertTrue(len(data['hotspots']) > 0)

    def test_nearby_sources_mumbai(self):
        res = self.client.get('/api/nearby-sources?city=Mumbai')
        self.assertEqual(res.status_code, 200)
        data = res.json['data']
        self.assertGreater(data['total_hotspots_found'], 0)

    def test_nearby_sources_arbitrary_coords(self):
        res = self.client.get('/api/nearby-sources?lat=12.97&lon=77.59&radius=25')
        self.assertEqual(res.status_code, 200)
        self.assertIn('data', res.json)

    def test_reverse_geocode(self):
        res = self.client.get('/api/reverse-geocode?lat=22.75&lon=88.34')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])
        self.assertEqual(res.json['locality'], 'Shrirampur')

    def test_realtime_air_quality(self):
        res = self.client.get('/api/realtime-air-quality?city=Delhi')
        self.assertEqual(res.status_code, 200)
        tel = res.json['telemetry']
        self.assertIn('pollutants', tel)
        self.assertIn('wind_speed_kmh', tel)

    def test_prediction_report(self):
        payload = {'PM2.5': 95.0, 'PM10': 150.0, 'NO2': 42.0}
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        rep = res.json['report']
        self.assertIn('pollutant_identification', rep)
        self.assertIn('source_attribution', rep)

    def test_partial_inputs_prediction(self):
        payload = {'PM2.5': 45.0}
        res = self.client.post('/api/predict', json=payload)
        self.assertEqual(res.status_code, 200)
        rep = res.json['report']
        self.assertIn('aqi', rep)

    def test_auth_workflow(self):
        # Fresh unauthenticated client
        fresh_client = app.app.test_client()
        res = fresh_client.get('/api/auth/status')
        self.assertEqual(res.status_code, 200)

        # Unauthenticated / redirects to /login
        redir_res = fresh_client.get('/')
        self.assertEqual(redir_res.status_code, 302)

        # Bad login via /login POST
        bad_login_page = fresh_client.post('/login', data={'username': 'wrong', 'password': 'bad'})
        self.assertEqual(bad_login_page.status_code, 200)
        self.assertIn('Invalid credentials', bad_login_page.text)

        # Bad login via /api/auth/login
        bad_res = fresh_client.post('/api/auth/login', json={'username': 'wrong', 'password': 'bad'})
        self.assertEqual(bad_res.status_code, 401)

        # Valid login via /api/auth/login with token
        token_res = fresh_client.post('/api/auth/login', json={'token': 'aero-intel-token-2026'})
        self.assertEqual(token_res.status_code, 200)
        self.assertTrue(token_res.json['is_admin'])

        # Logout via /logout route (redirects to /login)
        logout_route = fresh_client.get('/logout')
        self.assertEqual(logout_route.status_code, 302)
        self.assertIn('/login', logout_route.headers.get('Location', ''))

        # Valid login via /login POST form
        good_form = fresh_client.post('/login', data={'username': 'admin', 'password': 'admin123'})
        self.assertEqual(good_form.status_code, 302)
        self.assertIn('/', good_form.headers.get('Location', ''))

        # Once logged in, /login redirects to /
        already_logged = fresh_client.get('/login')
        self.assertEqual(already_logged.status_code, 302)

        # Valid login via /api/auth/login with user/pass
        good_res = fresh_client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        self.assertEqual(good_res.status_code, 200)
        self.assertTrue(good_res.json['is_admin'])

        res_after = fresh_client.get('/api/auth/status')
        self.assertTrue(res_after.json['is_admin'])

        logout_res2 = fresh_client.post('/api/auth/logout')
        self.assertEqual(logout_res2.status_code, 200)
        self.assertFalse(logout_res2.json['is_admin'])

    def test_tactical_enlarged_modal_and_controls(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Enlarged Map Modal elements
        self.assertIn('id="enlarged-map-modal"', html)
        self.assertIn('id="btn-enlarge-map-floating"', html)
        self.assertIn('id="btn-close-enlarged-map"', html)
        self.assertIn('id="modal-map-slot"', html)
        self.assertIn('id="modal-diagnostic-summary"', html)
        self.assertIn('id="btn-recenter-map"', html)

        # Confirm duplicate enlarge button is removed from card header
        self.assertNotIn('id="btn-enlarge-map"', html)

        # Green padlock beside operator
        self.assertIn('id="auth-status-icon"', html)
        self.assertIn('ph-lock-key text-emerald-400', html)

        # Fixed width and single-line sync button
        self.assertIn('id="btn-sync-realtime"', html)
        self.assertIn('whitespace-nowrap', html)
        self.assertIn('w-[140px]', html)

        # Hidden manual option in city selector
        self.assertIn('<option value="manual" disabled hidden>Manual</option>', html)
        self.assertIn('id="station-status-dot"', html)
        self.assertIn('id="station-prefix-label"', html)

    def test_favicons(self):
        # 1. Test root /favicon.ico route
        res_ico = self.client.get('/favicon.ico')
        self.assertEqual(res_ico.status_code, 200)
        self.assertIn('image', res_ico.content_type)
        res_ico.close()

        # 2. Test root /favicon.png and /favicon.svg routes
        res_png = self.client.get('/favicon.png')
        self.assertEqual(res_png.status_code, 200)
        res_png.close()

        res_svg = self.client.get('/favicon.svg')
        self.assertEqual(res_svg.status_code, 200)
        res_svg.close()

        # 3. Test static assets
        res_static_svg = self.client.get('/static/favicon.svg')
        self.assertEqual(res_static_svg.status_code, 200)
        res_static_svg.close()

        res_static_png = self.client.get('/static/favicon.png')
        self.assertEqual(res_static_png.status_code, 200)
        res_static_png.close()

        # 4. Test webmanifest
        res_manifest = self.client.get('/site.webmanifest')
        self.assertEqual(res_manifest.status_code, 200)
        self.assertIn('AeroIntel', res_manifest.text)
        res_manifest.close()

        # 5. Test template links
        res_idx = self.client.get('/')
        self.assertIn('favicon.svg', res_idx.text)
        self.assertIn('favicon.ico', res_idx.text)
        self.assertIn('site.webmanifest', res_idx.text)
        res_idx.close()

        unauth = app.app.test_client()
        res_log = unauth.get('/login')
        self.assertIn('favicon.svg', res_log.text)
        self.assertIn('site.webmanifest', res_log.text)
        res_log.close()

if __name__ == '__main__':
    unittest.main()
