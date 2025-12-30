"""Tests for script executor."""

from pathlib import Path

import pytest
from PIL import Image

from gen_art_framework import execute_script


class TestParameterInjection:
    """Tests for parameters being available as globals."""

    def test_parameters_available_as_globals(self, tmp_path: Path):
        """Parameters are accessible as global variables in the script."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
img = Image.new("RGB", (width, height), colour)
img
""")
        result = execute_script(script, {"width": 100, "height": 50, "colour": "red"})
        assert result.size == (100, 50)

    def test_empty_parameters(self, tmp_path: Path):
        """Script executes with empty parameters dict."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
Image.new("RGB", (10, 10))
""")
        result = execute_script(script, {})
        assert isinstance(result, Image.Image)


class TestResultCapture:
    """Tests for capturing the last expression."""

    def test_captures_last_expression(self, tmp_path: Path):
        """The final expression is captured and returned."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
a = Image.new("RGB", (10, 10), "blue")
b = Image.new("RGB", (20, 20), "red")
b
""")
        result = execute_script(script, {})
        assert result.size == (20, 20)

    def test_non_expression_final_statement(self, tmp_path: Path):
        """Raises error when final statement is not an expression."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
img = Image.new("RGB", (10, 10))
""")
        with pytest.raises(ValueError, match="must end with an expression"):
            execute_script(script, {})

    def test_expression_with_computation(self, tmp_path: Path):
        """Complex expressions work as final statement."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
Image.new("RGB", (5 * 2, 10))
""")
        result = execute_script(script, {})
        assert result.size == (10, 10)


class TestOutputValidation:
    """Tests for PIL Image output validation."""

    def test_valid_pil_image_succeeds(self, tmp_path: Path):
        """Returns PIL Image when script produces one."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
Image.new("RGBA", (100, 100))
""")
        result = execute_script(script, {})
        assert isinstance(result, Image.Image)

    def test_non_image_result_raises(self, tmp_path: Path):
        """Raises ValueError when result is not a PIL Image."""
        script = tmp_path / "script.py"
        script.write_text("""
"not an image"
""")
        with pytest.raises(ValueError, match="must return a PIL Image, got str"):
            execute_script(script, {})

    def test_none_result_raises(self, tmp_path: Path):
        """Raises ValueError when result is None."""
        script = tmp_path / "script.py"
        script.write_text("""
None
""")
        with pytest.raises(ValueError, match="must return a PIL Image, got None"):
            execute_script(script, {})

    def test_numeric_result_raises(self, tmp_path: Path):
        """Raises ValueError when result is a number."""
        script = tmp_path / "script.py"
        script.write_text("""
42
""")
        with pytest.raises(ValueError, match="must return a PIL Image, got int"):
            execute_script(script, {})


class TestErrorHandling:
    """Tests for script execution errors."""

    def test_script_exception_includes_traceback(self, tmp_path: Path):
        """Script exceptions include traceback in error message."""
        script = tmp_path / "script.py"
        script.write_text("""
def broken():
    raise RuntimeError("something went wrong")

broken()
""")
        with pytest.raises(ValueError, match="Script execution failed") as exc_info:
            execute_script(script, {})
        assert "RuntimeError: something went wrong" in str(exc_info.value)
        assert "broken()" in str(exc_info.value)

    def test_name_error_includes_traceback(self, tmp_path: Path):
        """Undefined variable errors include helpful traceback."""
        script = tmp_path / "script.py"
        script.write_text("""
undefined_variable
""")
        with pytest.raises(ValueError, match="Script execution failed") as exc_info:
            execute_script(script, {})
        assert "NameError" in str(exc_info.value)

    def test_syntax_error_raises(self, tmp_path: Path):
        """Syntax errors in script raise ValueError."""
        script = tmp_path / "script.py"
        script.write_text("""
def broken(
    pass
""")
        with pytest.raises(ValueError, match="Syntax error in script"):
            execute_script(script, {})

    def test_import_error_includes_traceback(self, tmp_path: Path):
        """Import errors include traceback."""
        script = tmp_path / "script.py"
        script.write_text("""
import nonexistent_module_xyz
""")
        with pytest.raises(ValueError, match="Script execution failed") as exc_info:
            execute_script(script, {})
        assert "ModuleNotFoundError" in str(exc_info.value)

    def test_script_not_found_raises(self, tmp_path: Path):
        """Raises ValueError when script file doesn't exist."""
        script = tmp_path / "nonexistent.py"
        with pytest.raises(ValueError, match="Script not found"):
            execute_script(script, {})

    def test_accepts_string_path(self, tmp_path: Path):
        """Accepts a string path as well as Path object."""
        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
Image.new("RGB", (10, 10))
""")
        result = execute_script(str(script), {})
        assert isinstance(result, Image.Image)

    def test_empty_script_raises(self, tmp_path: Path):
        """Raises ValueError for empty script."""
        script = tmp_path / "script.py"
        script.write_text("")
        with pytest.raises(ValueError, match="must end with an expression"):
            execute_script(script, {})

    def test_comment_only_script_raises(self, tmp_path: Path):
        """Raises ValueError for script with only comments."""
        script = tmp_path / "script.py"
        script.write_text("""
# This script only has comments
# No actual code
""")
        with pytest.raises(ValueError, match="must end with an expression"):
            execute_script(script, {})


class TestDistributionModeIntegration:
    """Integration tests for distribution mode with script execution."""

    def test_script_can_sample_from_distribution_parameter(self, tmp_path: Path):
        """Scripts can call .rvs() on distribution parameters."""
        from textwrap import dedent

        import numpy as np

        from gen_art_framework import parse_parameter_space, sample_parameter_space

        docstring = dedent("""
            parameters:
              - name: x_dist
                distribution: uniform
                loc: 0
                scale: 100
                mode: distribution
        """)

        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)
        params = sample_parameter_space(space, rng)

        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image
import numpy as np

# Sample multiple values from the distribution
values = [x_dist.rvs() for _ in range(5)]

# Use one of the values
width = int(values[0])
Image.new("RGB", (width, 50))
""")

        result = execute_script(script, params)
        assert isinstance(result, Image.Image)
        assert result.size[1] == 50
        assert 0 <= result.size[0] <= 100

    def test_distribution_mode_reproducibility_in_script(self, tmp_path: Path):
        """Distribution parameters produce reproducible results in scripts."""
        from textwrap import dedent

        import numpy as np

        from gen_art_framework import parse_parameter_space, sample_parameter_space

        docstring = dedent("""
            parameters:
              - name: colour_dist
                distribution: choice
                values: ["red", "green", "blue"]
                mode: distribution
        """)

        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image

# Sample colour multiple times
colours = [colour_dist.rvs() for _ in range(10)]

# Create image with first colour
Image.new("RGB", (10, 10), colours[0])
""")

        # Execute with same seed twice
        rng1 = np.random.default_rng(42)
        space1 = parse_parameter_space(docstring)
        params1 = sample_parameter_space(space1, rng1)
        result1 = execute_script(script, params1)

        rng2 = np.random.default_rng(42)
        space2 = parse_parameter_space(docstring)
        params2 = sample_parameter_space(space2, rng2)
        result2 = execute_script(script, params2)

        # Results should be identical (same colour selected)
        assert result1.getpixel((0, 0)) == result2.getpixel((0, 0))

    def test_mixed_sample_and_distribution_modes(self, tmp_path: Path):
        """Scripts can use both sampled values and distribution objects."""
        from textwrap import dedent

        import numpy as np

        from gen_art_framework import parse_parameter_space, sample_parameter_space

        docstring = dedent("""
            parameters:
              - name: width
                distribution: constant
                value: 100
                mode: sample
              - name: height_dist
                distribution: uniform
                loc: 50
                scale: 50
                mode: distribution
        """)

        space = parse_parameter_space(docstring)
        rng = np.random.default_rng(42)
        params = sample_parameter_space(space, rng)

        script = tmp_path / "script.py"
        script.write_text("""
from PIL import Image

# width is a sampled value (integer)
# height_dist is a distribution object
height = int(height_dist.rvs())

Image.new("RGB", (width, height))
""")

        result = execute_script(script, params)
        assert isinstance(result, Image.Image)
        assert result.size[0] == 100
        assert 50 <= result.size[1] <= 100
