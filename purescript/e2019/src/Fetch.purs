module Fetch where

import Prelude

import Data.Either (Either(..))
import Effect (Effect)
import Effect.Aff (Aff, makeAff, nonCanceler)
import Effect.Exception (error)

foreign import _fetchText ::
  String ->
  (String -> Effect Unit) ->
  (String -> Effect Unit) ->
  Effect Unit

foreign import setBodyHtml :: String -> Effect Unit

fetchText :: String -> Aff String
fetchText url = makeAff \k -> do
  _fetchText url
    (\text -> k (Right text))
    (\msg -> k (Left (error msg)))
  pure nonCanceler
