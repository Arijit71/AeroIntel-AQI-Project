import unittest
import app

class TestDOMElementsAndEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = app.app.test_client()
        with self.client.session_transaction() as sess:
            sess['is_authenticated'] = True
            sess['is_admin'] = True
            sess['username'] = 'admin'

    def test_unauthenticated_redirect_to_login(self):
        unauth_client = app.app.test_client()
        res = unauth_client.get('/')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/login', res.headers.get('Location', ''))

    def test_login_page_renders(self):
        unauth_client = app.app.test_client()
        res = unauth_client.get('/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn('AeroIntel Access Gateway', res.text)
        self.assertIn('Authenticate & Enter System', res.text)

    def test_dom_elements_present(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.text
        required_ids = [
            'aqi-form', 'select-city', 'btn-detect-gps', 'btn-sync-realtime',
            'aqi-score', 'gauge-progress-circle', 'category-banner', 'category-name',
            'dominant-pollutant-name', 'dominant-source-name', 'sources-map',
            'nearby-threat-count', 'nearby-diagnostic-text', 'nearby-hotspots-list',
            'source-attribution-bars', 'source-diagnostic-text', 'source-interventions-list',
            'health-advisory-text', 'sensitive-advisory-text', 'breakdown-bars',
            'btn-download-pdf', 'btn-auth-modal'
        ]
        for elem_id in required_ids:
            self.assertTrue(
                f'id="{elem_id}"' in html or f"id='{elem_id}'" in html,
                f"Missing required element ID in DOM: {elem_id}"
            )

        # Verify initial Mumbai baseline alignment
        self.assertIn('<option value="Mumbai" selected>Mumbai</option>', html)
        self.assertIn('Bandra Kurla Complex (MPCB)', html)
        self.assertIn('16.0 km/h', html)
        self.assertIn('240° (WSW)', html)
        self.assertIn('spectrum-indicator-dot', html)

    def test_api_predict(self):
        res = self.client.post('/api/predict', json={'PM2.5': 95.0, 'PM10': 140.0})
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

    def test_nearby_sources(self):
        res = self.client.get('/api/nearby-sources?city=Delhi')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json['success'])

if __name__ == '__main__':
    unittest.main()
