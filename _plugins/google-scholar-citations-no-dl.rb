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
      # Evaluate article_id from context manually
      article_id_var = @article_id.strip
      article_id = nil
      
      if article_id_var.include?('.')
        parts = article_id_var.split('.')
        base = context[parts[0]]
        if base
          # Handle both Hash-like and Object-like base objects
          if base.respond_to?(:[]) && !base[parts[1]].nil?
            article_id = base[parts[1]]
          elsif base.respond_to?(parts[1])
            article_id = base.send(parts[1])
          end
        end
      else
        article_id = context[article_id_var]
      end
      
      # Fallback to the raw string if nothing was found
      article_id = article_id_var if article_id.nil? || article_id.to_s.strip.empty?
      article_id = article_id.to_s.strip
      
      puts "[DEBUG] Looking up pub_id: #{article_id}, found: #{citations[article_id]}"
      citations.fetch(article_id, "N/A")
    end
  end
end

Liquid::Template.register_tag('google_scholar_citations_no_dl', Jekyll::GoogleScholarCitationsTag)