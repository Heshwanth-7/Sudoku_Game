import unittest

from app import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.c = app.test_client()
        r = self.c.post("/api/games", json={"difficulty": "easy"})
        self.assertEqual(r.status_code, 201)
        self.g = r.get_json()
        self.gid = self.g["id"]
        self.base = f"/api/games/{self.gid}"

    def empty_cell(self):
        for r in range(9):
            for c in range(9):
                if self.g["puzzle"][r][c] == 0:
                    return r, c

    def test_frontend_served(self):
        self.assertEqual(self.c.get("/").status_code, 200)
        self.assertEqual(self.c.get("/app.js").status_code, 200)

    def test_solution_not_leaked(self):
        self.assertNotIn("solution", self.g)

    def test_move_undo_redo(self):
        r, c = self.empty_cell()
        s = self.c.post(self.base + "/move", json={"row": r, "col": c, "value": 5}).get_json()
        self.assertEqual(s["board"][r][c], 5)
        self.assertTrue(s["can_undo"])
        s = self.c.post(self.base + "/undo").get_json()
        self.assertEqual(s["board"][r][c], 0)
        s = self.c.post(self.base + "/redo").get_json()
        self.assertEqual(s["board"][r][c], 5)

    def test_errors(self):
        r = self.c.post(self.base + "/undo")
        self.assertEqual(r.status_code, 400)
        given = next((i, j) for i in range(9) for j in range(9) if self.g["puzzle"][i][j])
        r = self.c.post(self.base + "/move", json={"row": given[0], "col": given[1], "value": 1})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.c.get("/api/games/nope").status_code, 404)
        self.assertEqual(self.c.post("/api/games", json={"difficulty": "x"}).status_code, 400)

    def test_hint_check_analysis_history(self):
        h = self.c.post(self.base + "/hint").get_json()
        self.assertEqual(h["hints"], 1)
        self.assertIn("hint", h)
        r, c = self.empty_cell()
        wrong_val = 1 if h["board"][r][c] != 1 else 2
        self.c.post(self.base + "/move", json={"row": r, "col": c, "value": wrong_val})
        chk = self.c.get(self.base + "/check").get_json()["wrong"]
        a = self.c.get(self.base + "/analysis").get_json()
        self.assertEqual(a["hints used"], 1)
        self.assertGreaterEqual(len(self.c.get(self.base + "/history").get_json()), 2)
        self.assertIsInstance(chk, list)

    def test_give_up(self):
        s = self.c.post(self.base + "/solve").get_json()
        self.assertTrue(s["solved"] and s["revealed"])


if __name__ == "__main__":
    unittest.main()
