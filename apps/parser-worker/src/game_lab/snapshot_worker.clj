(ns game-lab.snapshot-worker
  "Read-only gd-edit save parser entry point for the Game Lab API."
  (:require [clojure.data.json :as json]
            [clojure.java.io :as io]
            [gd-edit.io.gdc :as gdc]
            [gd-edit.io.stash :as stash])
  (:import (java.nio.charset StandardCharsets)))

(def ^:private max-input-bytes (* 16 1024 1024))
(def ^:private max-output-bytes (* 16 1024 1024))

(def ^:private item-fields
  [:basename
   :prefix-name
   :suffix-name
   :modifier-name
   :transmute-name
   :seed
   :relic-name
   :relic-bonus
   :relic-seed
   :augment-name
   :augment-bonus
   :augment-seed
   :ascended-name
   :ascended-bonus
   :relic-completion-level
   :stack-count
   :seed-reroll-count
   :affix-reroll-count
   :X
   :Y])

(defn- item-projection [item]
  (into {}
        (keep (fn [field]
                (when (contains? item field)
                  [(name field) (get item field)])))
        item-fields))

(defn- character-projection [character]
  {"character-name" (:character-name character)
   "character-level" (:character-level character)
   "hardcore-mode" (:hardcore-mode character)
   "meta-fileinfo"
   {"data-version" (get-in character [:meta-fileinfo :data-version])}
   "equipment" (mapv item-projection (:equipment character))
   "inventory-sacks"
   (mapv (fn [sack]
           {"inventory-items" (mapv item-projection (:inventory-items sack))})
         (:inventory-sacks character))
   "stashes"
   (mapv (fn [tab]
           {"items" (mapv item-projection (:items tab))})
         (:stashes character))})

(defn- shared-stash-projection [shared-stash]
  (when-not (= 18 (:meta-block-id shared-stash))
    (throw (ex-info "not a transfer stash" {})))
  {"version" (:version shared-stash)
   "stash"
   (mapv (fn [tab]
           {"inventory-items" (mapv item-projection (:inventory-items tab))})
         (:stash shared-stash))})

(defn- parse-file [source-type file]
  (case source-type
    "character" (character-projection (gdc/load-character-file* (.getPath file)))
    "sharedStash" (shared-stash-projection (stash/load-stash-file (.getPath file)))
    (throw (ex-info "unsupported source type" {}))))

(defn -main [& args]
  (try
    (when-not (= 2 (count args))
      (throw (ex-info "invalid arguments" {})))
    (let [[source-type file-path] args
          file (io/file file-path)]
      (when-not (.isFile file)
        (throw (ex-info "input is not a regular file" {})))
      (when (> (.length file) max-input-bytes)
        (throw (ex-info "input exceeds size limit" {})))
      (let [encoded (json/write-str (parse-file source-type file))
            encoded-size (alength (.getBytes encoded StandardCharsets/UTF_8))]
        (when (> encoded-size max-output-bytes)
          (throw (ex-info "output exceeds size limit" {})))
        (println encoded)))
    (catch Throwable _
      ;; Never print parser exceptions: they can include local paths or input data.
      (binding [*out* *err*]
        (println "snapshot parser rejected input"))
      (System/exit 2))))
