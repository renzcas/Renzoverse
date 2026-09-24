$dirs = @(
    "core\engine\event-bus",
    "core\engine\state-manager",
    "core\engine\physics",
    "core\engine\ai",
    "core\engine\mythic-runtime",
    "core\assets\textures",
    "core\assets\models",
    "core\assets\sounds",
    "core\assets\shaders",

    "cave-world\levels\level1",
    "cave-world\levels\level2",
    "cave-world\levels\level3",
    "cave-world\levels\volcano-lake",
    "cave-world\labyrinth",
    "cave-world\trog",
    "cave-world\conan",
    "cave-world\odysseus",
    "cave-world\aeneas",
    "cave-world\golden-bough",

    "surface-world\hydra",
    "surface-world\beasts",
    "surface-world\temples",
    "surface-world\mythic-quests",

    "cyber-world\ww3\factions\graywatch",
    "cyber-world\ww3\factions\federal",
    "cyber-world\ww3\factions\darknet",
    "cyber-world\ww3\factions\civlib",
    "cyber-world\ww3\missions",
    "cyber-world\ww3\corridors",
    "cyber-world\ww3\maps",

    "cyber-world\darknet\corridors",
    "cyber-world\darknet\nodes",
    "cyber-world\darknet\signals",

    "cyber-world\hacker-lab\challenges",
    "cyber-world\hacker-lab\opcodes",
    "cyber-world\hacker-lab\reverse",
    "cyber-world\hacker-lab\cyber-range",

    "sovereign-world\big-animal\instinct-map",
    "sovereign-world\big-animal\bosses",
    "sovereign-world\big-animal\sovereign-behaviors",

    "sovereign-world\sovereign-engine\decrees",
    "sovereign-world\sovereign-engine\vectors",
    "sovereign-world\sovereign-engine\hybrid",

    "sovereign-world\world-state",

    "agentdash\panels\cave",
    "agentdash\panels\cyber",
    "agentdash\panels\sovereign",
    "agentdash\panels\mythic",
    "agentdash\ui",

    "site\docs",
    "site\labs",
    "site\mythic",

    "docs\design",
    "docs\lore",
    "docs\quests",
    "docs\architecture"
)

foreach ($d in $dirs) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

New-Item -ItemType File -Path "site\index.html" -Force | Out-Null
New-Item -ItemType File -Path "site\game.html" -Force | Out-Null
New-Item -ItemType File -Path "README.md" -Force | Out-Null
