# `Apache Hive UDF` 事始め

## Apache Hive UDFって何？
Hive はHiveSQLで操作すると思うんですが（まずこの文章が分からない人はHiveとはなんぞ、ということを調べてねっ）その時既存のHive MallなどのUDFではちょっと物足りなくて、新しい機能を作りたい！　という人のために用意された、機能拡張関数のことです。
UDFはUser Defined Functionの略です。
例えば:
```
SELECT str, upper(str) FROM table1…
```
の時、小文字を大文字に変えるUDF upperを使うことができます。
この（怪しい）関数っぽい機能のことをUDFと言います。

## この文章について
Apache Hive UDFの作り方を伝授する目的で作られた文書です。

## 対象読者
Apache Hive UDF に興味がある人、あるいは実際にHive UDFを作ることになった人で、Java か Scala を解する人を対象としています。


## 簡単にまとめると
`org.apache.hadoop.hive.ql.udf.generic.GenericUDF`を継承するクラスを作ります（それだけ）。
いくつかUDFにも種類があるのですがここでは標準的なものを対象とします。
aggregate の機能を有するものなどについては、UDAFなどで調べると出てきます。英語がほとんどです。

### 初期化
```
@Override
  public ObjectInspector initialize(ObjectInspector[](#) arguments) throws UDFArgumentException 
}
```
この中でやる。
### 実際の呼び出し
```
@Override
  public Object evaluate(DeferredObject[](#) arguments) throws HiveException 
}
```
evaluateメソッドの中でレコードの入力カラムを受け取り、
結果を返す。

## 以上

## だとちょっと不親切なので

意外とGenericUDFなどがあるディレクトリ内に存在するJavaファイルがほぼ全部特定ケースUDFのためのクラスなので、これを（パクって）参考にして自分のUDFを書くといいです。割と複雑なものまで準備されています。

## native （CやC++など）の関数をつかいたい
正直あまり勧めませんが（なぜかと言うとデバッグが大変困難なので）、そう言うこともあります。その時はstatic節（最初の最初に初期化される）で、System.load()かSystem.loadLibrary()を使ってDLL（Linuxの場合dynamic library）を読み込みます。
loadの方は絶対pathの指定が必要ですが、トラブルが少ないです。

## initializeメソッド
実際のspark-hive-udf-mecabを例にとって見てみます。
```
@Override
  public ObjectInspector initialize(ObjectInspector[](#) arguments) throws UDFArgumentException 
// This UDF accepts one argument
assert (arguments.length == 1);
```
なくてもいいんですが、ここでまず受け付けるargumentsが一つだけ、と言うことを確認します。
```
// The first argument is a primitive type
assert(arguments[0](#).getCategory() == Category.PRIMITIVE);
this.inputOI  = (PrimitiveObjectInspector)arguments[0](#);
```
argumentsの0番目要素のカテゴリーが、プリミティブ（整数や文字列）であることを保証します。
そしてそのことを確認した上で、ObjectInspector -\> PrimitiveObjectInspector のダウンキャストをします。
```
GenericUDFUtils.ReturnObjectInspectorResolver returnOIResolver = new GenericUDFUtils.ReturnObjectInspectorResolver(true);
returnOI = returnOIResolver.get(PrimitiveObjectInspectorFactory.javaStringObjectInspector);
// 
```
ResolverはGenericUDFUtilsにあるReturnObjectInspectorResolverを初期化して使います。trueはなんだったか忘れました（ぉぃw）。
もう一つ、inputOIの代わりにUDFの返り値のためのreturnOIを用意します。javaStringObjectInspector を PrimitiveObjectInspectorFactoryで生成して、それをresolverに渡します。
```
System.out.println("java.library.path="+System.getProperty("java.library.path"));
Tagger tagger2 = null;
if (this.tagger == null) 
try 
System.err.println("Powered by MeCab: Version " + MeCab.VERSION);
try 
// tagger2 = new Tagger("-Ochasen -d /home/hadoop/spark-hive-udf-mecab/mecab/lib/mecab/dic/");
//// tagger2 = new Tagger();
this.model = new Model();
this.tagger = this.model.createTagger();
//this.lattice = model.createLattice();

} catch (java.lang.Exception e) 
System.err.println("catch RuntimeError:");
e.printStackTrace();
tagger2 = null;
}
} catch (UnsatisfiedLinkError e) 
System.err.println("Cannot load the example native code.nMake sure your LD_LIBRARY_PATH contains '.'n" + e);
System.err.println("*** I would like to stop this program with exit.nbut I can not...");
tagger2 = null;
}
//System.err.println("tagger2="+tagger2.hashCode());
this.tagger = tagger2;
}
```
ここまで長いですが、libmecab（形態素解析ライブラリ）の初期化そのものを持ってきましたので参考にしてください。
なお、この中で読んでいるクラスは、あらかじめimportするのですが、
別途JarファイルなどでJava bindingsを提供してもらう必要があります。今回はmecabがJava bindingsを用意していたので、それを使うだけですが、自分が作ったC系関数の場合、Java wrapperが必要です（めんどいw）。

```
（ファイル冒頭）
import org.chasen.mecab.MeCab;
import org.chasen.mecab.Tagger;
import org.chasen.mecab.Model;
import org.chasen.mecab.Lattice;
import org.chasen.mecab.Node;

```

最後に、文字列のリストを返すので、それに合ったObjectInspectorを返してあげます。ObjectInspectorFactoryにいっぱいメソッドがあって、getStandardListObjectInspectorがリストを返すOIです。
この時なんのリストを返すかが必要で、returnOIに入っているresolverで処理されたOIを入れて、Java Stringのリストが返ることを明言します。

```
return ObjectInspectorFactory.getStandardListObjectInspector(returnOI);
  }
```

実際簡単なUDFならこんなに複雑になりませんが、一応少し難しい例を例示しました。

## evaluateメソッド
実際の個々のケースの計算は毎回evaluateメソッドが呼ばれ、都度結果を返します。ここは高速に動くことを前提に書かなければならない部分です。

```
@Override
  public Object evaluate(DeferredObject[](#) arguments) throws HiveException 
/* We only support STRING type */
assert(this.inputOI.getPrimitiveCategory() == PrimitiveCategory.STRING);
```
まず、input argumentsのカテゴリーが文字列であることを保証します。
evaluateにはObjectInspectorではなく、DefeffedObject すなわちブツそのものが入ってきます。

```
/* And we'll return a type int, so let's return the corresponding object inspector */
this.outputOI = PrimitiveObjectInspectorFactory.writableStringObjectInspector;
```
outputOIとして、writableStringObjectInspectorを生成します。
returnOIと違う型になっているのに注意してください。
```
ret.clear();
Object oin = arguments[0](#).get();
```
実際に渡ってきた文字列をラップしたオブジェクトをoinに入れます。
```
if (oin == null) return null;
```
ヌルチェックしましょう。

```
String value = (String)this.inputOI.getPrimitiveJavaObject(oin);
```
実際のStringはinputOI経由でPrimitiveJavaObjectを取り出し、結果的にダウンキャストされます。
```
ArrayList\<Object\> words = new ArrayList\<Object\>();
```

結果を詰めるArrayListを作ります。このwordsに結果を詰めて送り出します。

```
Node node = null;
if (value == null) 
return words;
}
if (this.tagger == null)  // recovery...even broken...
MecabSurface.duplicateload();
this.model = new Model();
this.tagger = this.model.createTagger();
}
node = this.tagger.parseToNode(value);
if (node == null) 
return words; // null for irregular cases.
}
for (;node != null; node = node.getNext()) 
StringBuffer sb = new StringBuffer(node.getSurface());
String w = sb.toString();
if (w.length() \> 0) 
words.add(w);
}
}
return words;
  }
```
以上長かったですが、形態素解析の処理をして、wordsにStringを複数入れて返します。StringBufferを経由しているのはmecabがコピーを作らないでポインタを使い回すので一回抜けると内容が変わってしまうことを回避するためにやっていますが、いらないかもしれません。

```
  @Override
  public String getDisplayString(String[](#) children) 
return getStandardDisplayString("array", children, ",");
  }
}
```
表示の仕方を指定します。arrayであること、文字列を”,”で区切ることなどを表現します。

## 実際の運用

```
ADD JAR MeCab.jar;
ADD JAR spark-hive-udf_2.10-0.1.0.jar;
```
ADD JAR でjar ファイルをHive SQL上で指定します。
```
CREATE TEMPORARY FUNCTION surface AS 'com.ardentex.spark.hiveudf.MecabSurface';
```
FUNCTIONを作ります。JAR内のクラス（GenericUDFを拡張したクラス）を指定します。

```
SELECT keyword, surface(keyword) FROM full_query WHERE ver='2018-06-01' AND sub_ver='00-00-00';
```

作ったUDF(surfaceという名前になっていて、これはどんな名前にでもできる）はこんな感じで呼びます。

## ビルド
基本的にGenericUDFがコンパイルできればどんなやり方でも構いませんが、僕はScalaも使える出来合いのサンプルを持ってきて改良してします。シェルスクリプトを起動すると自動的にJarファイルを作ってくれるので、あとはJavaなりScalaでUDFのクラスを書いて入れるだけです。


## 以上
(^^ゞ

