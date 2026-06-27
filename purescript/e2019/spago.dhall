{ name = "aoc-2019"
, dependencies =
    [ "aff"
    , "arrays"
    , "console"
    , "effect"
    , "either"
    , "foldable-traversable"
    , "integers"
    , "maybe"
    , "prelude"
    , "strings"
    , "web-dom"
    , "web-events"
    , "web-html"
    ]
, packages = ./packages.dhall
, sources = [ "src/**/*.purs" ]
}
