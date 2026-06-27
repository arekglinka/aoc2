module Main where

import Prelude

import Data.Array (filter, mapMaybe)
import Data.Foldable (sum)
import Data.Int (fromString)
import Data.String (Pattern(..), split, trim)
import Effect (Effect)
import Effect.Aff (launchAff_)
import Effect.Class (liftEffect)
import Fetch (fetchText, setBodyHtml)

main :: Effect Unit
main = launchAff_ do
  content <- fetchText "../../../data/e2019/day1.txt"
  let masses = parseMasses content
      part1 = sum (map fuelFromMass masses)
      part2 = sum (map totalFuel masses)
  liftEffect $ setBodyHtml (renderHtml part1 part2)

parseMasses :: String -> Array Int
parseMasses content =
  mapMaybe fromString
    $ filter (notEq "")
    $ map trim
    $ split (Pattern "\n") content

fuelFromMass :: Int -> Int
fuelFromMass mass = mass / 3 - 2

totalFuel :: Int -> Int
totalFuel mass = go mass 0
  where
    go current total =
      let fuel = fuelFromMass current
      in if fuel <= 0 then total
         else go fuel (total + fuel)

renderHtml :: Int -> Int -> String
renderHtml part1 part2 =
  "<h1>AoC 2019 Day 1 — Rocket Equation</h1>\
   \<p><strong>Part 1:</strong> " <> show part1 <> "</p>\
   \<p><strong>Part 2:</strong> " <> show part2 <> "</p>"

