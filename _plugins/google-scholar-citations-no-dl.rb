require "active_support/all"
require 'nokogiri'
require 'open-uri'
require 'csv'

module Helpers
  extend ActiveSupport::NumberHelper
end

module Jekyll
  class GoogleScholarCitationsTag < Liquid::Tag
    def initialize(tag_name, params, tokens)
      super
      splitted = params.split(" ").map(&:strip)
      @scholar_id = splitted[0]
      @article_id = splitted[1]
    end

    def render(context)
      site = context.registers[:site]
      csv_path = File.join(site.source, '_data', 'scholar_citations.csv')
      citations = {}
      if File.exist?(csv_path)
        CSV.foreach(csv_path, headers: true) do |row|
          citations[row['pub_id'].to_s.strip] = row['citations'].to_s.strip
        end
      end
      article_id = @article_id.to_s.strip
      puts "[DEBUG] Looking up pub_id: #{article_id}, found: #{citations[article_id]}"
      citations.fetch(article_id, "N/A")
    end
  end
end

Liquid::Template.register_tag('google_scholar_citations_no_dl', Jekyll::GoogleScholarCitationsTag)