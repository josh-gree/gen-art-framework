"""Tests for the CLI."""

from pathlib import Path

from click.testing import CliRunner

from gen_art_framework.cli import cli


SAMPLE_SCRIPT = '''"""
parameters:
  - name: width
    distribution: constant
    value: 100
  - name: height
    distribution: constant
    value: 100
  - name: colour
    distribution: choice
    values: ["red", "blue", "green"]
"""
from PIL import Image
Image.new("RGB", (width, height), colour)
'''


class TestHelpOutput:
    """Tests for --help output."""

    def test_main_help(self):
        """Main CLI shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Gen-art-framework" in result.output
        assert "sample" in result.output

    def test_sample_help(self):
        """Sample command shows help."""
        runner = CliRunner()
        result = runner.invoke(cli, ["sample", "--help"])
        assert result.exit_code == 0
        assert "--count" in result.output
        assert "--output" in result.output
        assert "--seed" in result.output


class TestBasicGeneration:
    """Tests for basic image generation."""

    def test_generates_single_image(self, tmp_path: Path):
        """Generates one image with default count."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output_dir = tmp_path / "output"

        runner = CliRunner()
        result = runner.invoke(
            cli, ["sample", str(script), "--output", str(output_dir), "--seed", "42"]
        )

        assert result.exit_code == 0
        images = list(output_dir.glob("*.png"))
        assert len(images) == 1

    def test_generates_multiple_images(self, tmp_path: Path):
        """Generates specified number of images."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output_dir = tmp_path / "output"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "sample",
                str(script),
                "--count",
                "5",
                "--output",
                str(output_dir),
                "--seed",
                "42",
            ],
        )

        assert result.exit_code == 0
        images = list(output_dir.glob("*.png"))
        assert len(images) == 5

    def test_creates_output_directory(self, tmp_path: Path):
        """Creates output directory if it doesn't exist."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output_dir = tmp_path / "nested" / "output" / "dir"

        runner = CliRunner()
        result = runner.invoke(
            cli, ["sample", str(script), "--output", str(output_dir), "--seed", "42"]
        )

        assert result.exit_code == 0
        assert output_dir.exists()


class TestSeedReproducibility:
    """Tests for seed handling and reproducibility."""

    def test_same_seed_produces_same_output(self, tmp_path: Path):
        """Same seed produces identical images."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output1 = tmp_path / "output1"
        output2 = tmp_path / "output2"

        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "sample",
                str(script),
                "--count",
                "3",
                "--output",
                str(output1),
                "--seed",
                "12345",
            ],
        )
        runner.invoke(
            cli,
            [
                "sample",
                str(script),
                "--count",
                "3",
                "--output",
                str(output2),
                "--seed",
                "12345",
            ],
        )

        images1 = sorted(output1.glob("*.png"))
        images2 = sorted(output2.glob("*.png"))

        assert len(images1) == len(images2) == 3

        for img1, img2 in zip(images1, images2):
            assert img1.read_bytes() == img2.read_bytes()

    def test_different_seeds_produce_different_filenames(self, tmp_path: Path):
        """Different seeds produce different filenames."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output1 = tmp_path / "output1"
        output2 = tmp_path / "output2"

        runner = CliRunner()
        runner.invoke(
            cli, ["sample", str(script), "--output", str(output1), "--seed", "111"]
        )
        runner.invoke(
            cli, ["sample", str(script), "--output", str(output2), "--seed", "222"]
        )

        name1 = list(output1.glob("*.png"))[0].name
        name2 = list(output2.glob("*.png"))[0].name

        assert name1 != name2


class TestFilenameFormat:
    """Tests for output filename format."""

    def test_filename_format(self, tmp_path: Path):
        """Filenames follow <script_name>_<index>_<seed>.png format."""
        script = tmp_path / "my_script.py"
        script.write_text(SAMPLE_SCRIPT)
        output_dir = tmp_path / "output"

        runner = CliRunner()
        runner.invoke(
            cli,
            [
                "sample",
                str(script),
                "--count",
                "3",
                "--output",
                str(output_dir),
                "--seed",
                "42",
            ],
        )

        images = sorted(output_dir.glob("*.png"))
        assert len(images) == 3

        for i, img in enumerate(images):
            parts = img.stem.split("_")
            assert parts[0] == "my"
            assert parts[1] == "script"
            # Index part
            assert parts[2] == str(i)
            # Seed part (integer)
            int(parts[3])


class TestProgressOutput:
    """Tests for progress output."""

    def test_progress_output(self, tmp_path: Path):
        """Progress messages are output."""
        script = tmp_path / "script.py"
        script.write_text(SAMPLE_SCRIPT)
        output_dir = tmp_path / "output"

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "sample",
                str(script),
                "--count",
                "2",
                "--output",
                str(output_dir),
                "--seed",
                "42",
            ],
        )

        assert result.exit_code == 0
        assert "Generating image 1/2" in result.output
        assert "Generating image 2/2" in result.output
        assert "Generated 2 image(s)" in result.output


class TestErrorHandling:
    """Tests for error conditions."""

    def test_missing_docstring(self, tmp_path: Path):
        """Error for script without docstring."""
        script = tmp_path / "script.py"
        script.write_text("from PIL import Image\nImage.new('RGB', (10, 10))")

        runner = CliRunner()
        result = runner.invoke(cli, ["sample", str(script)])

        assert result.exit_code != 0
        assert "no docstring" in result.output

    def test_invalid_parameter_space(self, tmp_path: Path):
        """Error for invalid YAML in docstring."""
        script = tmp_path / "script.py"
        script.write_text('''"""
not valid yaml for parameters
"""
from PIL import Image
Image.new("RGB", (10, 10))
''')

        runner = CliRunner()
        result = runner.invoke(cli, ["sample", str(script)])

        assert result.exit_code != 0
        assert "Failed to parse parameter space" in result.output

    def test_nonexistent_script(self, tmp_path: Path):
        """Error for non-existent script file."""
        runner = CliRunner()
        result = runner.invoke(cli, ["sample", str(tmp_path / "nonexistent.py")])

        assert result.exit_code != 0

    def test_syntax_error_in_script(self, tmp_path: Path):
        """Error for script with syntax error."""
        script = tmp_path / "script.py"
        script.write_text("def broken(\n")

        runner = CliRunner()
        result = runner.invoke(cli, ["sample", str(script)])

        assert result.exit_code != 0
        assert "syntax error" in result.output
