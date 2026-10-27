from game import TILE, Game, should_record_loss

def test_render_png(): assert Game().render().startswith(b"\x89PNG")
def test_won_false(): assert Game().is_won() is False
def test_won_corner():
    g = Game(); g.player_x = 2*(g.cols-1)*TILE+TILE//2; g.player_y = 2*(g.rows-1)*TILE+TILE//2
    assert g.is_won() is True
def test_block():
    g = Game(); x, y = g.player_x, g.player_y
    assert g.move("up") is False and g.move("left") is False
    assert (g.player_x, g.player_y) == (x, y) and g.moves == 0
def test_loss_no_game(): assert should_record_loss(None, False, 123.0) is False
def test_loss_won(): assert should_record_loss(object(), True, 123.0) is False
def test_loss_no_moves(): assert should_record_loss(object(), False, None) is False
def test_loss_yes(): assert should_record_loss(object(), False, 123.0) is True
